import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

from apps.users.models import Permission

permissions = [
    Permission(name='Show Role', code_name='show_role', module_name='Role', module_label='User Management', description='User can see role'),
    Permission(name='Create Role', code_name='create_role', module_name='Role', module_label='User Management', description='User can create role'),
    Permission(name='Read Role', code_name='read_role', module_name='Role', module_label='User Management', description='User can read role'),
    Permission(name='Update Role', code_name='update_role', module_name='Role', module_label='User Management', description='User can update role'),
    Permission(name='Delete Role', code_name='delete_role', module_name='Role', module_label='User Management', description='User can delete role'),

    Permission(name='Show User', code_name='show_user', module_name='User', module_label='User Management',
               description='User can see user'),
    Permission(name='Create User', code_name='create_user', module_name='User', module_label='User Management',
               description='User can create user'),
    Permission(name='Read User', code_name='read_user', module_name='User', module_label='User Management',
               description='User can read user'),
    Permission(name='Update User', code_name='update_user', module_name='User', module_label='User Management',
               description='User can update user'),
    Permission(name='Delete User', code_name='delete_user', module_name='User', module_label='User Management',
               description='User can delete user'),
    Permission(name='Deactivate User', code_name='toggle_user', module_name='User', module_label='User Management',
               description='User can deactivate user'),

#         # ---------- CATEGORY ----------
#     Permission(name='Create Category', code_name='create_category', module_name='Category', module_label='Blog Management',
#             description='User can create category'),
#     Permission(name='Read Category', code_name='read_category', module_name='Category', module_label='Blog Management',
#             description='User can read category'),
#     Permission(name='Update Category', code_name='update_category', module_name='Category', module_label='Blog Management',
#             description='User can update category'),
#     Permission(name='Delete Category', code_name='delete_category', module_name='Category', module_label='Blog Management',
#             description='User can delete category'),

#     # ---------- TAG ----------
#     Permission(name='Create Tag', code_name='create_tag', module_name='Tag', module_label='Blog Management',
#             description='User can create tag'),
#     Permission(name='Read Tag', code_name='read_tag', module_name='Tag', module_label='Blog Management',
#             description='User can read tag'),
#     Permission(name='Update Tag', code_name='update_tag', module_name='Tag', module_label='Blog Management',
#             description='User can update tag'),
#     Permission(name='Delete Tag', code_name='delete_tag', module_name='Tag', module_label='Blog Management',
#             description='User can delete tag'),

#     # ---------- BLOG POST ----------
#     Permission(name='Create Blog Post', code_name='create_blog_post', module_name='BlogPost', module_label='Blog Management',
#             description='User can create blog post'),
#     Permission(name='Read Blog Post', code_name='read_blog_post', module_name='BlogPost', module_label='Blog Management',
#             description='User can read blog post'),
#     Permission(name='Update Blog Post', code_name='update_blog_post', module_name='BlogPost', module_label='Blog Management',
#             description='User can update blog post'),
#     Permission(name='Delete Blog Post', code_name='delete_blog_post', module_name='BlogPost', module_label='Blog Management',
#             description='User can delete blog post'),

#     # ---------- COMMENT ----------
#     Permission(name='Create Comment', code_name='create_comment', module_name='Comment', module_label='Blog Management',
#             description='User can create comment'),
#     Permission(name='Read Comment', code_name='read_comment', module_name='Comment', module_label='Blog Management',
#             description='User can read comment'),
#     Permission(name='Update Comment', code_name='update_comment', module_name='Comment', module_label='Blog Management',
#             description='User can update comment'),
#     Permission(name='Delete Comment', code_name='delete_comment', module_name='Comment', module_label='Blog Management',
#             description='User can delete comment'),

#     # ---------- MEDIA ----------
#     Permission(name='Create Media', code_name='create_media', module_name='Media', module_label='Media Library',
#             description='User can create media'),
#     Permission(name='Read Media', code_name='read_media', module_name='Media', module_label='Media Library',
#             description='User can read media'),
#     Permission(name='Update Media', code_name='update_media', module_name='Media', module_label='Media Library',
#             description='User can update media'),
#     Permission(name='Delete Media', code_name='delete_media', module_name='Media', module_label='Media Library',
#             description='User can delete media'),

#     # ---------- NEWSLETTER ----------
#     Permission(name='Create Newsletter', code_name='create_newsletter', module_name='Newsletter', module_label='Campaign Management',
#             description='User can create newsletter'),
#     Permission(name='Read Newsletter', code_name='read_newsletter', module_name='Newsletter', module_label='Campaign Management',
#             description='User can read newsletter'),
#     Permission(name='Update Newsletter', code_name='update_newsletter', module_name='Newsletter', module_label='Campaign Management',
#             description='User can update newsletter'),
#     Permission(name='Delete Newsletter', code_name='delete_newsletter', module_name='Newsletter', module_label='Campaign Management',
#             description='User can delete newsletter'),

#     # ---------- CAMPAIGN ----------
#     Permission(name='Create Campaign', code_name='create_campaign', module_name='Campaign', module_label='Campaign Management',
#             description='User can create campaign'),
#     Permission(name='Read Campaign', code_name='read_campaign', module_name='Campaign', module_label='Campaign Management',
#             description='User can read campaign'),
#     Permission(name='Update Campaign', code_name='update_campaign', module_name='Campaign', module_label='Campaign Management',
#             description='User can update campaign'),
#     Permission(name='Delete Campaign', code_name='delete_campaign', module_name='Campaign', module_label='Campaign Management',
#             description='User can delete campaign'),

    # ---------- Image ----------
    Permission(name='Create Image', code_name='create_image', module_name='Image', module_label='Image Management',
            description='User can create Image'),
    Permission(name='Read Image', code_name='read_image', module_name='Image', module_label='Image Management',
            description='User can read Image'),
    Permission(name='Update Image', code_name='update_image', module_name='Image', module_label='Image Management',
            description='User can update Image'),
    Permission(name='Delete Image', code_name='delete_image', module_name='Image', module_label='Image Management',
            description='User can delete Image'),

            # ---------- Category ----------
    Permission(name='Create Image Category', code_name='create_image_category', module_name='Image Category', module_label=' Image Category Management',
            description='User can create Image Category'),
    Permission(name='Read Image Category', code_name='read_image_category', module_name='Image Category', module_label='Image Category Management',
            description='User can read Image Category'),
    Permission(name='Update Image Category', code_name='update_image_category', module_name='Image Category', module_label='Image Category Management',
            description='User can update Image Category'),
    Permission(name='Delete Image Category', code_name='delete_image_category', module_name='Image Category', module_label='Image Category Management',
            description='User can delete Image Category'),

                # ---------- Student ----------
        Permission(name='Create Student', code_name='create_student', module_name='Student', module_label='Student Management',
                description='User can create Student'),
        Permission(name='Read Student', code_name='read_student', module_name='Student', module_label='Student Management',
                description='User can read Student'),
        Permission(name='Update Student', code_name='update_student', module_name='Student', module_label='Student Management',
                description='User can update Student'),
        Permission(name='Delete Student', code_name='delete_student', module_name='Student', module_label='Student Management',
                description='User can delete Student'),

        # ---------- Teacher ----------
        Permission(name='Create Teacher', code_name='create_teacher', module_name='Teacher', module_label='Teacher Management',
                description='User can create Teacher'),
        Permission(name='Read Teacher', code_name='read_teacher', module_name='Teacher', module_label='Teacher Management',
                description='User can read Teacher'),
        Permission(name='Update Teacher', code_name='update_teacher', module_name='Teacher', module_label='Teacher Management',
                description='User can update Teacher'),
        Permission(name='Delete Teacher', code_name='delete_teacher', module_name='Teacher', module_label='Teacher Management',
                description='User can delete Teacher'),

        # ---------- Parent ----------
        Permission(name='Create Parent', code_name='create_parent', module_name='Parent', module_label='Parent Management',
                description='User can create Parent'),
        Permission(name='Read Parent', code_name='read_parent', module_name='Parent', module_label='Parent Management',
                description='User can read Parent'),
        Permission(name='Update Parent', code_name='update_parent', module_name='Parent', module_label='Parent Management',
                description='User can update Parent'),
        Permission(name='Delete Parent', code_name='delete_parent', module_name='Parent', module_label='Parent Management',
                description='User can delete Parent'),

        # ---------- AcademicYear ----------
        Permission(name='Create Academic Year', code_name='create_academic_year', module_name='AcademicYear', module_label='Academic Year Management', description='User can create Academic Year'),
        Permission(name='Read Academic Year', code_name='read_academic_year', module_name='AcademicYear', module_label='Academic Year Management', description='User can read Academic Year'),
        Permission(name='Update Academic Year', code_name='update_academic_year', module_name='AcademicYear', module_label='Academic Year Management', description='User can update Academic Year'),
        Permission(name='Delete Academic Year', code_name='delete_academic_year', module_name='AcademicYear', module_label='Academic Year Management', description='User can delete Academic Year'),

        # ---------- Department ----------
        Permission(name='Create Department', code_name='create_department', module_name='Department', module_label='Department Management', description='User can create Department'),
        Permission(name='Read Department', code_name='read_department', module_name='Department', module_label='Department Management', description='User can read Department'),
        Permission(name='Update Department', code_name='update_department', module_name='Department', module_label='Department Management', description='User can update Department'),
        Permission(name='Delete Department', code_name='delete_department', module_name='Department', module_label='Department Management', description='User can delete Department'),

        # ---------- Class ----------
        Permission(name='Create Class', code_name='create_class', module_name='Class', module_label='Class Management', description='User can create Class'),
        Permission(name='Read Class', code_name='read_class', module_name='Class', module_label='Class Management', description='User can read Class'),
        Permission(name='Update Class', code_name='update_class', module_name='Class', module_label='Class Management', description='User can update Class'),
        Permission(name='Delete Class', code_name='delete_class', module_name='Class', module_label='Class Management', description='User can delete Class'),

        # ---------- Section ----------
        Permission(name='Create Section', code_name='create_section', module_name='Section', module_label='Section Management', description='User can create Section'),
        Permission(name='Read Section', code_name='read_section', module_name='Section', module_label='Section Management', description='User can read Section'),
        Permission(name='Update Section', code_name='update_section', module_name='Section', module_label='Section Management', description='User can update Section'),
        Permission(name='Delete Section', code_name='delete_section', module_name='Section', module_label='Section Management', description='User can delete Section'),

        # ---------- Subject ----------
        Permission(name='Create Subject', code_name='create_subject', module_name='Subject', module_label='Subject Management', description='User can create Subject'),
        Permission(name='Read Subject', code_name='read_subject', module_name='Subject', module_label='Subject Management', description='User can read Subject'),
        Permission(name='Update Subject', code_name='update_subject', module_name='Subject', module_label='Subject Management', description='User can update Subject'),
        Permission(name='Delete Subject', code_name='delete_subject', module_name='Subject', module_label='Subject Management', description='User can delete Subject'),

        # ---------- ClassSubject ----------
        Permission(name='Create Class Subject', code_name='create_classsubject', module_name='ClassSubject', module_label='Class Subject Management', description='User can create Class Subject'),
        Permission(name='Read Class Subject', code_name='read_classsubject', module_name='ClassSubject', module_label='Class Subject Management', description='User can read Class Subject'),
        Permission(name='Update Class Subject', code_name='update_classsubject', module_name='ClassSubject', module_label='Class Subject Management', description='User can update Class Subject'),
        Permission(name='Delete Class Subject', code_name='delete_classsubject', module_name='ClassSubject', module_label='Class Subject Management', description='User can delete Class Subject'),

        # ---------- DailyAttendance ----------
        Permission(name='Create Daily Attendance', code_name='create_daily_attendance', module_name='DailyAttendance', module_label='Daily Attendance Management', description='User can create Daily Attendance'),
        Permission(name='Read Daily Attendance', code_name='read_daily_attendance', module_name='DailyAttendance', module_label='Daily Attendance Management', description='User can read Daily Attendance'),
        Permission(name='Update Daily Attendance', code_name='update_daily_attendance', module_name='DailyAttendance', module_label='Daily Attendance Management', description='User can update Daily Attendance'),
        Permission(name='Delete Daily Attendance', code_name='delete_daily_attendance', module_name='DailyAttendance', module_label='Daily Attendance Management', description='User can delete Daily Attendance'),

        # ---------- MonthlyAttendanceReport ----------
        Permission(name='Create Monthly Attendance Report', code_name='create_monthly_attendance_report', module_name='MonthlyAttendanceReport', module_label='Monthly Attendance Report Management', description='User can create Monthly Attendance Report'),
        Permission(name='Read Monthly Attendance Report', code_name='read_monthly_attendance_report', module_name='MonthlyAttendanceReport', module_label='Monthly Attendance Report Management', description='User can read Monthly Attendance Report'),
        Permission(name='Update Monthly Attendance Report', code_name='update_monthly_attendance_report', module_name='MonthlyAttendanceReport', module_label='Monthly Attendance Report Management', description='User can update Monthly Attendance Report'),
        Permission(name='Delete Monthly Attendance Report', code_name='delete_monthly_attendance_report', module_name='MonthlyAttendanceReport', module_label='Monthly Attendance Report Management', description='User can delete Monthly Attendance Report'),

        # ---------- AttendanceConfiguration ----------
        Permission(name='Create Attendance Configuration', code_name='create_attendance_configuration', module_name='AttendanceConfiguration', module_label='Attendance Configuration Management', description='User can create Attendance Configuration'),
        Permission(name='Read Attendance Configuration', code_name='read_attendance_configuration', module_name='AttendanceConfiguration', module_label='Attendance Configuration Management', description='User can read Attendance Configuration'),
        Permission(name='Update Attendance Configuration', code_name='update_attendance_configuration', module_name='AttendanceConfiguration', module_label='Attendance Configuration Management', description='User can update Attendance Configuration'),
        Permission(name='Delete Attendance Configuration', code_name='delete_attendance_configuration', module_name='AttendanceConfiguration', module_label='Attendance Configuration Management', description='User can delete Attendance Configuration'),

        # ---------- AttendanceSummary ----------
        Permission(name='Create Attendance Summary', code_name='create_attendance_summary', module_name='AttendanceSummary', module_label='Attendance Summary Management', description='User can create Attendance Summary'),
        Permission(name='Read Attendance Summary', code_name='read_attendance_summary', module_name='AttendanceSummary', module_label='Attendance Summary Management', description='User can read Attendance Summary'),
        Permission(name='Update Attendance Summary', code_name='update_attendance_summary', module_name='AttendanceSummary', module_label='Attendance Summary Management', description='User can update Attendance Summary'),
        Permission(name='Delete Attendance Summary', code_name='delete_attendance_summary', module_name='AttendanceSummary', module_label='Attendance Summary Management', description='User can delete Attendance Summary'),

        # ---------- TimeSlot ----------
        Permission(name='Create Time Slot', code_name='create_time_slot', module_name='TimeSlot', module_label='Time Slot Management', description='User can create Time Slot'),
        Permission(name='Read Time Slot', code_name='read_time_slot', module_name='TimeSlot', module_label='Time Slot Management', description='User can read Time Slot'),
        Permission(name='Update Time Slot', code_name='update_time_slot', module_name='TimeSlot', module_label='Time Slot Management', description='User can update Time Slot'),
        Permission(name='Delete Time Slot', code_name='delete_time_slot', module_name='TimeSlot', module_label='Time Slot Management', description='User can delete Time Slot'),

        # ---------- Timetable ----------
        Permission(name='Create Timetable', code_name='create_time_table', module_name='Timetable', module_label='Timetable Management', description='User can create Timetable'),
        Permission(name='Read Timetable', code_name='read_time_table', module_name='Timetable', module_label='Timetable Management', description='User can read Timetable'),
        Permission(name='Update Timetable', code_name='update_time_table', module_name='Timetable', module_label='Timetable Management', description='User can update Timetable'),
        Permission(name='Delete Timetable', code_name='delete_time_table', module_name='Timetable', module_label='Timetable Management', description='User can delete Timetable'),
]


def add_permission():
    for permission in permissions:
        try:
            Permission.objects.get(code_name=permission.code_name)
        except Permission.DoesNotExist:
            permission.save()


if __name__ == '__main__':
    print("Populating Permissions ...")
    add_permission()