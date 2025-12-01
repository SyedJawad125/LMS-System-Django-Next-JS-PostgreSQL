from datetime import date
from rest_framework import serializers
from .models import Announcement, Event, Message, Notification
from apps.academic.serializers import ClassListingSerializer
from apps.users.serializers import UserListSerializer


# ==================== Announcement Serializers ====================

class AnnouncementListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for announcement listings"""
    published_by_name = serializers.SerializerMethodField()
    target_class_name = serializers.CharField(source='target_class.name', read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'announcement_type', 'target_audience',
            'target_class_name', 'is_active', 'published_by_name', 'published_at'
        ]
    
    def get_published_by_name(self, obj):
        if obj.published_by:
            full_name = obj.published_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.published_by.username
        return None


class AnnouncementSerializer(serializers.ModelSerializer):
    """Full announcement serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    published_by_detail = serializers.SerializerMethodField()
    target_class_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'announcement_type', 'target_audience',
            'target_class', 'attachment', 'is_active', 'published_by',
            'published_at', 'published_by_detail', 'target_class_detail',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('published_at', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_published_by_detail(self, obj):
        if obj.published_by and not obj.published_by.deleted:
            return UserListSerializer(obj.published_by).data
        return None
    
    def get_target_class_detail(self, obj):
        if obj.target_class and not obj.target_class.deleted:
            return ClassListingSerializer(obj.target_class).data
        return None
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long")
        return value.strip()
    
    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters long")
        return value.strip()
    
    def validate_target_class(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted class")
        return value
    
    def validate_published_by(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted user")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        target_audience = data.get('target_audience', getattr(self.instance, 'target_audience', None))
        target_class = data.get('target_class', getattr(self.instance, 'target_class', None))
        
        # If target audience is SPECIFIC_CLASS, target_class must be provided
        if target_audience == 'SPECIFIC CLASS':
            if not target_class:
                raise serializers.ValidationError({
                    'target_class': 'Target class is required when target audience is "SPECIFIC CLASS"'
                })
        else:
            # Clear target_class if not SPECIFIC_CLASS
            if target_class:
                data['target_class'] = None
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'title': instance.title,
                'message': f'Announcement "{instance.title}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        if isinstance(data.get('published_at'), str):
            data['published_at'] = data['published_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Event Serializers ====================

class EventListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for event listings"""
    organizer_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'event_type', 'start_date', 'end_date',
            'venue', 'organizer_name', 'is_published', 'status'
        ]
    
    def get_organizer_name(self, obj):
        if obj.organizer:
            full_name = obj.organizer.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.organizer.username
        return None
    
    def get_status(self, obj):
        """Determine event status based on dates"""
        today = date.today()
        if obj.start_date > today:
            return 'Upcoming'
        elif obj.end_date < today:
            return 'Completed'
        elif obj.start_date <= today <= obj.end_date:
            return 'Ongoing'
        return 'Unknown'


class EventSerializer(serializers.ModelSerializer):
    """Full event serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    organizer_detail = serializers.SerializerMethodField()
    target_classes_detail = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type', 'start_date',
            'end_date', 'venue', 'organizer', 'target_classes', 'image',
            'is_published', 'organizer_detail', 'target_classes_detail',
            'status', 'duration_days',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_organizer_detail(self, obj):
        if obj.organizer and not obj.organizer.deleted:
            return UserListSerializer(obj.organizer).data
        return None
    
    def get_target_classes_detail(self, obj):
        classes = obj.target_classes.filter(deleted=False)
        return ClassListingSerializer(classes, many=True).data
    
    def get_status(self, obj):
        """Determine event status based on dates"""
        today = date.today()
        if obj.start_date > today:
            return 'upcoming'
        elif obj.end_date < today:
            return 'completed'
        elif obj.start_date <= today <= obj.end_date:
            return 'ongoing'
        return 'unknown'
    
    def get_duration_days(self, obj):
        """Calculate event duration in days"""
        return (obj.end_date - obj.start_date).days + 1
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long")
        return value.strip()
    
    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long")
        return value.strip()
    
    def validate_venue(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Venue must be at least 2 characters long")
        return value.strip()
    
    def validate_organizer(self, value):
        if value and value.deleted:
            raise serializers.ValidationError("Cannot use a deleted user")
        return value
    
    def validate_start_date(self, value):
        """Validate start date is not too far in the past"""
        if value < date.today():
            # Allow past dates for record keeping, but warn if too old
            days_old = (date.today() - value).days
            if days_old > 365:
                raise serializers.ValidationError("Start date is more than a year in the past")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = data.get('end_date', getattr(self.instance, 'end_date', None))
        
        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError({
                    'end_date': 'End date must be on or after start date'
                })
            
            # Check duration isn't too long (optional business rule)
            duration = (end_date - start_date).days
            if duration > 365:
                raise serializers.ValidationError({
                    'end_date': 'Event duration cannot exceed 365 days'
                })
        
        return data
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'title': instance.title,
                'message': f'Event "{instance.title}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Message Serializers ====================

class MessageListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for message listings"""
    sender_name = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender_name', 'recipient_name', 'subject',
            'is_read', 'sent_at'
        ]
    
    def get_sender_name(self, obj):
        if obj.sender:
            full_name = obj.sender.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.sender.username
        return None
    
    def get_recipient_name(self, obj):
        if obj.recipient:
            full_name = obj.recipient.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.recipient.username
        return None


class MessageSerializer(serializers.ModelSerializer):
    """Full message serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    sender_detail = serializers.SerializerMethodField()
    recipient_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'recipient', 'subject', 'body',
            'attachment', 'is_read', 'read_at', 'sent_at',
            'sender_detail', 'recipient_detail',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('sent_at', 'read_at', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_sender_detail(self, obj):
        if obj.sender and not obj.sender.deleted:
            return UserListSerializer(obj.sender).data
        return None
    
    def get_recipient_detail(self, obj):
        if obj.recipient and not obj.recipient.deleted:
            return UserListSerializer(obj.recipient).data
        return None
    
    def validate_subject(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Subject must be at least 3 characters long")
        return value.strip()
    
    def validate_body(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message body must be at least 10 characters long")
        return value.strip()
    
    def validate_sender(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted user as sender")
        return value
    
    def validate_recipient(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot use a deleted user as recipient")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        sender = data.get('sender', getattr(self.instance, 'sender', None))
        recipient = data.get('recipient', getattr(self.instance, 'recipient', None))
        
        if sender and recipient:
            # Prevent sending message to self
            if sender.id == recipient.id:
                raise serializers.ValidationError({
                    'recipient': 'Cannot send message to yourself'
                })
        
        return data
    
    def create(self, validated_data):
        """Mark message as unread on creation"""
        validated_data['is_read'] = False
        validated_data['read_at'] = None
        return super().create(validated_data)
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'subject': instance.subject,
                'message': f'Message "{instance.subject}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        if isinstance(data.get('sent_at'), str):
            data['sent_at'] = data['sent_at'].replace('T', ' ').split('.')[0]
        if data.get('read_at') and isinstance(data.get('read_at'), str):
            data['read_at'] = data['read_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Notification Serializers ====================

class NotificationListingSerializer(serializers.ModelSerializer):
    """Minimal serializer for notification listings"""
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user_name', 'notification_type', 'title',
            'is_read', 'created_at'
        ]
    
    def get_user_name(self, obj):
        if obj.user:
            full_name = obj.user.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.user.username
        return None


class NotificationSerializer(serializers.ModelSerializer):
    """Full notification serializer with validations"""
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    user_detail = serializers.SerializerMethodField()
    time_since = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'title', 'message',
            'link', 'is_read', 'user_detail', 'time_since',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_created_by(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.created_by.username
        return None
    
    def get_updated_by(self, obj):
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            return full_name.strip() if full_name and full_name.strip() else obj.updated_by.username
        return None
    
    def get_user_detail(self, obj):
        if obj.user and not obj.user.deleted:
            return UserListSerializer(obj.user).data
        return None
    
    def get_time_since(self, obj):
        """Calculate human-readable time since notification was created"""
        from datetime import datetime, timezone
        
        # Ensure created_at is timezone-aware
        now = datetime.now(timezone.utc)
        created = obj.created_at
        
        if created.tzinfo is None:
            # If created_at is naive, make it aware
            created = created.replace(tzinfo=timezone.utc)
        
        diff = now - created
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long")
        return value.strip()
    
    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long")
        return value.strip()
    
    def validate_user(self, value):
        if value.deleted:
            raise serializers.ValidationError("Cannot create notification for a deleted user")
        return value
    
    def validate_link(self, value):
        """Validate link format if provided"""
        if value:
            # Basic URL validation - you can make this more sophisticated
            if not value.startswith(('/', 'http://', 'https://')):
                raise serializers.ValidationError("Link must be a valid URL or path")
        return value
    
    def create(self, validated_data):
        """Mark notification as unread on creation"""
        validated_data['is_read'] = False
        return super().create(validated_data)
    
    def to_representation(self, instance):
        if instance.deleted:
            return {
                'id': instance.id,
                'title': instance.title,
                'message': f'Notification "{instance.title}" has been deleted successfully'
            }
        
        data = super().to_representation(instance)
        
        # Format datetime fields
        if isinstance(data.get('created_at'), str):
            data['created_at'] = data['created_at'].replace('T', ' ').split('.')[0]
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = data['updated_at'].replace('T', ' ').split('.')[0]
        
        return data


# ==================== Bulk Operations Serializers ====================

class BulkNotificationSerializer(serializers.Serializer):
    """Serializer for creating bulk notifications"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of user IDs to send notification to"
    )
    notification_type = serializers.ChoiceField(choices=Notification.NOTIFICATION_TYPES)
    title = serializers.CharField(min_length=3, max_length=200)
    message = serializers.CharField(min_length=10)
    link = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate_user_ids(self, value):
        """Validate all user IDs exist and are not deleted"""
        from apps.users.models import User
        
        existing_users = User.objects.filter(id__in=value, deleted=False)
        if existing_users.count() != len(value):
            invalid_ids = set(value) - set(existing_users.values_list('id', flat=True))
            raise serializers.ValidationError(
                f"Invalid or deleted user IDs: {list(invalid_ids)}"
            )
        return value
    
    def create(self, validated_data):
        """Create notifications for all specified users"""
        user_ids = validated_data.pop('user_ids')
        notifications = []
        
        for user_id in user_ids:
            notification = Notification.objects.create(
                user_id=user_id,
                **validated_data
            )
            notifications.append(notification)
        
        return notifications


class MarkMessagesReadSerializer(serializers.Serializer):
    """Serializer for marking multiple messages as read"""
    message_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of message IDs to mark as read"
    )
    
    def validate_message_ids(self, value):
        """Validate all message IDs exist and belong to the current user"""
        user = self.context.get('request').user if self.context.get('request') else None
        if not user:
            raise serializers.ValidationError("User context required")
        
        messages = Message.objects.filter(
            id__in=value,
            recipient=user,
            deleted=False
        )
        
        if messages.count() != len(value):
            invalid_ids = set(value) - set(messages.values_list('id', flat=True))
            raise serializers.ValidationError(
                f"Invalid message IDs or not owned by user: {list(invalid_ids)}"
            )
        
        return value
    
    def save(self):
        """Mark all specified messages as read"""
        from django.utils import timezone
        
        message_ids = self.validated_data['message_ids']
        updated_count = Message.objects.filter(
            id__in=message_ids
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return updated_count