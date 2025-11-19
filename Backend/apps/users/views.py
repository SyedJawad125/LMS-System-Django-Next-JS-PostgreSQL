from rest_framework.views import APIView
from rest_framework.response import Response
from utils.reusable_functions import (create_response, get_first_error, get_tokens_for_user)
from rest_framework import status
from utils.response_messages import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (LoginSerializer, LoginUserSerializer, EmptySerializer, LogoutSerializer,
                          SetPasswordSerializer, PermissionSerializer, EmployeeSerializer,
                          UserSerializer, RoleSerializer, RoleListingSerializer)
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from config.settings import (SIMPLE_JWT, FRONTEND_BASE_URL, PASSWORD_RESET_VALIDITY, FRONTEND_EMAIL_LINK)
from .models import UserToken, User
from django.utils import timezone
from utils.helpers import generate_token
from apps.notification.tasks import send_email
from utils.enums import *
from django.db import transaction
from utils.base_api import BaseView
from collections import defaultdict
from utils.decorator import permission_required
from utils.permission_enums import *
from .filters import (EmployeeFilter, RoleFilter)


class LoginView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data, context={'request': request})
            if serialized_data.is_valid():
                user = serialized_data.validated_data['user']
                tokens = get_tokens_for_user(user)
                resp_data = LoginUserSerializer(user, context={'tokens': tokens}).data
                return Response(create_response(SUCCESSFUL, resp_data), status=status.HTTP_200_OK)
            else:
                return Response(create_response(get_first_error(serialized_data.errors)),
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response(create_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RefreshView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = EmptySerializer

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(create_response(REFRESH_TOKEN_NOT_FOUND), status=status.HTTP_401_UNAUTHORIZED)
            try:
                refresh = RefreshToken(refresh_token)
            except Exception as e:
                print(str(e))
                return Response(create_response(SESSION_EXPIRED), status=status.HTTP_401_UNAUTHORIZED)
            new_access_token = AccessToken()
            new_access_token['user_id'] = refresh['user_id']
            new_access_token.set_exp(lifetime=SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])
            token_payload = new_access_token.payload
            # # extra check
            # try:
            #     token_payload = AccessToken(new_access_token).payload
            # except Exception as e:
            #     print(str(e))
            resp_data = {
                "refresh_token": refresh_token,
                "access_token": str(new_access_token)
            }
            return Response(create_response(SUCCESSFUL, resp_data), status=status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
            return Response(create_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request):
        try:
            serialized_data = LogoutSerializer(data=request.data, context={'request': request})
            if serialized_data.is_valid():
                request.user.last_login = timezone.now()
                request.user.save()
                UserToken.objects.filter(user=request.user).update(device_token=None)
                return Response(create_response(SUCCESSFUL), status=status.HTTP_200_OK)
            else:
                return Response(create_response(get_first_error(serialized_data.errors)),
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response(create_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ForgetPasswordView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = EmptySerializer

    def post(self, request):
        try:
            email = request.data.get('email')
            if email:
                user = User.objects.filter(email=email, deleted=False).first()
                if user:
                    self.forget_email(user)
                    return Response(create_response(SUCCESSFUL), status=status.HTTP_200_OK)
                else:
                    return Response(create_response(INVALID_EMAIL), status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(create_response(EMAIL_NOT_PROVIDED), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response(create_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def forget_email(user):
        token_string = f"{user.id}_{user.username}"
        token = generate_token(token_string)
        user.password_link_token = token
        user.password_link_token_created_at = timezone.now()
        user.is_active = False
        user.is_blocked = True
        user.save()
        # http: // localhost: 5173 / verify - link /?method = reset_password
        # url = f"{FRONTEND_BASE_URL}/password/reset/{str(user.password_link_token)}"
        url = f"{FRONTEND_EMAIL_LINK}/{str(user.password_link_token)}"
        send_email.delay(FORGET_PASSWORD_EMAIL_TEMP, [user.email], {"full_name": user.full_name, "url": url, "validity": PASSWORD_RESET_VALIDITY})


class VerifyLinkView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = EmptySerializer

    def post(self, request):
        try:
            if request.data.get('token'):
                resp = {
                    "token": request.data.get('token'),
                    "redirect_password": False,
                    "redirect_activate_account": False,
                }
                user = User.objects.filter(password_link_token=request.data.get('token'), deleted=False).first()
                if user:
                    validate_till = user.password_link_token_created_at + timezone.timedelta(
                        hours=PASSWORD_RESET_VALIDITY)
                    if timezone.now() > validate_till:
                        user.password_link_token = None
                        user.password_link_token_created_at = None
                        user.save()
                        return Response(create_response(LINK_EXPIRED), status=status.HTTP_400_BAD_REQUEST)
                    else:
                        resp['redirect_password'] = True
                elif not user:
                    user = User.objects.filter(activation_link_token=request.data.get('token'), deleted=False).first()
                    if not user:
                        return Response(create_response(LINK_EXPIRED), status=status.HTTP_400_BAD_REQUEST)
                    resp['redirect_activate_account'] = True
                return Response(create_response(SUCCESSFUL, resp), status=status.HTTP_200_OK)
            else:
                return Response(create_response(TOKEN_NOT_PROVIDED), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response(create_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = SetPasswordSerializer

    def post(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                instance = User.objects.filter(password_link_token=request.data.get('token'), deleted=False).first()
                if instance:
                    if instance.check_password(serialized_data.validated_data.get('new_password')):
                        return Response(create_response(NEW_PASSWORD_IS_SAME_AS_OLD),
                                        status=status.HTTP_400_BAD_REQUEST)
                    instance.set_password(serialized_data.validated_data.get('new_password'))
                    instance.password_link_token = None
                    instance.password_link_token_created_at = None
                    instance.is_active = True
                    instance.is_blocked = False
                    instance.last_password_changed = timezone.now()
                    instance.save()
                    return Response(create_response(SUCCESSFUL, {"redirect_login": True}), status=status.HTTP_200_OK)
                else:
                    return Response(create_response(LINK_EXPIRED), status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(create_response(get_first_error(serialized_data.errors)),
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response(create_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployeeView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmployeeSerializer
    filterset_class = EmployeeFilter

    @permission_required([CREATE_USER])
    def post(self, request):
        try:
            resp = super().post_(request)
            if resp.status_code == status.HTTP_201_CREATED:
                self.invitation_email(request, resp.data.get('data'))
            return resp
        except Exception as e:
            print(str(e))
            return Response(create_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def invitation_email(request, resp_data):
        token = resp_data.pop('activation_link_token')
        context = {
            "full_name": resp_data.get('full_name'),
            "url": f"{FRONTEND_EMAIL_LINK}/{token}",
            "sender_name": request.user.full_name,
        }
        send_email.delay(USER_INVITATION, [resp_data.get('email')], context)

    @permission_required([READ_USER])
    def get(self, request):
        return super().get_(request)

    @permission_required([DELETE_USER])
    def delete(self, request):
        try:
            if request.query_params.get('id'):
                instance = self.serializer_class.Meta.model.objects.filter(deleted=False,
                                                                           id=request.query_params.get('id',
                                                                                                       None)).first()
                if instance:
                    with transaction.atomic():
                        instance.deleted = True
                        instance.updated_by = request.user
                        instance.save()
                        instance.user.delete()
                        serialized_resp = self.serializer_class(instance, context={'request': request}).data
                        self.delete_email(request.user, serialized_resp)
                    return Response(create_response(SUCCESSFUL, serialized_resp), status=status.HTTP_200_OK)
                else:
                    return Response(create_response(NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(create_response(ID_NOT_PROVIDED), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response(create_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def delete_email(request_user, resp_data):
        context = {
            "full_name": resp_data.get('full_name'),
            "sender_name": request_user.full_name,
        }
        send_email.delay(USER_DELETE_EMAIL_TEMP, [resp_data.get('email')], context)


class EmployeeToggleView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmployeeSerializer
    filterset_class = None

    @permission_required([TOGGLE_USER])
    def delete(self, request):
        try:
            if request.query_params.get('id'):
                instance = self.serializer_class.Meta.model.objects.filter(deleted=False,
                                                                           id=request.query_params.get('id',
                                                                                                       None)).first()
                if instance:
                    with transaction.atomic():
                        template = USER_RE_ACTIVATED_EMAIL_TEMP
                        if instance.status == DEACTIVATED and instance.user.password:
                            instance.status = ACTIVE
                            instance.user.deactivated = False
                        elif instance.status == DEACTIVATED and not instance.user.password:
                            instance.status = INVITED
                            instance.user.deactivated = False
                        else:
                            template = USER_DEACTIVATED_EMAIL_TEMP
                            instance.status = DEACTIVATED
                            instance.user.deactivated = True
                        instance.updated_by = request.user
                        instance.user.save()
                        instance.save()
                    self.notification_email(request.user, instance.user, template)
                    resp_data = self.serializer_class(instance, context={'request': request}).data
                    return Response(create_response(SUCCESSFUL, resp_data), status=status.HTTP_200_OK)
                else:
                    return Response(create_response(NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(create_response(ID_NOT_PROVIDED), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response(create_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def notification_email(request_user, user_instance, template):
        context = {
            "full_name": user_instance.full_name,
            "sender_name": request_user.full_name,
        }
        send_email.delay(template, [user_instance.email], context)


class PermissionView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PermissionSerializer

    @permission_required([CREATE_ROLE])
    def get(self, request):
        try:
            permissions = self.serializer_class.Meta.model.objects.all()
            serialized_data = PermissionSerializer(permissions, many=True).data
            grouped_data = defaultdict(list)
            for item in serialized_data:
                module_label = item.get("module_label", "Uncategorized")
                grouped_data[module_label].append(item)
            return Response(create_response(SUCCESSFUL, grouped_data, permissions.count()), status=status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
            return Response(create_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoleView(BaseView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RoleSerializer
    filterset_class = RoleFilter
    list_serializer = RoleListingSerializer

    @permission_required([CREATE_ROLE])
    def post(self, request):
        return super().post_(request)

    @permission_required([READ_ROLE])
    def get(self, request):
        return super().get_(request)

    @permission_required([UPDATE_ROLE])
    def patch(self, request):
        return super().patch_(request)

    @permission_required([DELETE_ROLE])
    def delete(self, request):
        try:
            if request.query_params.get('id'):
                instance = self.serializer_class.Meta.model.objects.filter(deleted=False,
                                                                           id=request.query_params.get('id',
                                                                                                       None)).first()
                if instance:
                    if instance.role_users.filter(deleted=False).exists():
                        return Response(create_response(USERS_ASSOCIATED_WITH_THIS_ROLE), status=status.HTTP_400_BAD_REQUEST)
                    instance.deleted = True
                    instance.updated_by = request.user
                    instance.save()
                    serialized_resp = self.serializer_class(instance).data
                    return Response(create_response(SUCCESSFUL, serialized_resp), status=status.HTTP_200_OK)
                else:
                    return Response(create_response(NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(create_response(ID_NOT_PROVIDED), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response(create_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccountActivateView(BaseView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = SetPasswordSerializer

    def post(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                instance = User.objects.filter(activation_link_token=request.data.get('token'), deleted=False).first()
                if instance:
                    with transaction.atomic():
                        instance.set_password(serialized_data.validated_data.get('new_password'))
                        instance.activation_link_token = None
                        instance.activation_link_token_created_at = None
                        instance.is_active = True
                        instance.is_blocked = False
                        instance.is_verified = True
                        instance.user_employee.status = ACTIVE
                        instance.user_employee.save()
                        instance.last_password_changed = timezone.now()
                        instance.save()
                    return Response(create_response(SUCCESSFUL, {"redirect_login": True}), status=status.HTTP_200_OK)
                else:
                    return Response(create_response(LINK_EXPIRED), status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(create_response(get_first_error(serialized_data.errors)),
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response(create_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
