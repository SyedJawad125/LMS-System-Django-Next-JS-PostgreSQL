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

        # ---------- Exam Type ----------
        Permission(name='Create Exam Type', code_name='create_exam_type', module_name='Exam Type', module_label='Examination Management', description='User can create Exam Type'),
        Permission(name='Read Exam Type', code_name='read_exam_type', module_name='Exam Type', module_label='Examination Management', description='User can read Exam Type'),
        Permission(name='Update Exam Type', code_name='update_exam_type', module_name='Exam Type', module_label='Examination Management', description='User can update Exam Type'),
        Permission(name='Delete Exam Type', code_name='delete_exam_type', module_name='Exam Type', module_label='Examination Management', description='User can delete Exam Type'),

        # ---------- Exam ----------
        Permission(name='Create Exam', code_name='create_exam', module_name='Exam', module_label='Examination Management', description='User can create Exam'),
        Permission(name='Read Exam', code_name='read_exam', module_name='Exam', module_label='Examination Management', description='User can read Exam'),
        Permission(name='Update Exam', code_name='update_exam', module_name='Exam', module_label='Examination Management', description='User can update Exam'),
        Permission(name='Delete Exam', code_name='delete_exam', module_name='Exam', module_label='Examination Management', description='User can delete Exam'),

        # ---------- Exam Schedule ----------
        Permission(name='Create Exam Schedule', code_name='create_exam_schedule', module_name='Exam Schedule', module_label='Examination Management', description='User can create Exam Schedule'),
        Permission(name='Read Exam Schedule', code_name='read_exam_schedule', module_name='Exam Schedule', module_label='Examination Management', description='User can read Exam Schedule'),
        Permission(name='Update Exam Schedule', code_name='update_exam_schedule', module_name='Exam Schedule', module_label='Examination Management', description='User can update Exam Schedule'),
        Permission(name='Delete Exam Schedule', code_name='delete_exam_schedule', module_name='Exam Schedule', module_label='Examination Management', description='User can delete Exam Schedule'),

        # ---------- Exam Result ----------
        Permission(name='Create Exam Result', code_name='create_exam_result', module_name='Exam Result', module_label='Examination Management', description='User can create Exam Result'),
        Permission(name='Read Exam Result', code_name='read_exam_result', module_name='Exam Result', module_label='Examination Management', description='User can read Exam Result'),
        Permission(name='Update Exam Result', code_name='update_exam_result', module_name='Exam Result', module_label='Examination Management', description='User can update Exam Result'),
        Permission(name='Delete Exam Result', code_name='delete_exam_result', module_name='Exam Result', module_label='Examination Management', description='User can delete Exam Result'),

        # ---------- Grade System ----------
        Permission(name='Create Grade System', code_name='create_grade_system', module_name='Grade System', module_label='Examination Management', description='User can create Grade System'),
        Permission(name='Read Grade System', code_name='read_grade_system', module_name='Grade System', module_label='Examination Management', description='User can read Grade System'),
        Permission(name='Update Grade System', code_name='update_grade_system', module_name='Grade System', module_label='Examination Management', description='User can update Grade System'),
        Permission(name='Delete Grade System', code_name='delete_grade_system', module_name='Grade System', module_label='Examination Management', description='User can delete Grade System'),

        # ---------- Fee Type ----------
        Permission(name='Create Fee Type', code_name='create_fee_type', module_name='Fee Type', module_label='Fee Management', description='User can create Fee Type'),
        Permission(name='Read Fee Type', code_name='read_fee_type', module_name='Fee Type', module_label='Fee Management', description='User can read Fee Type'),
        Permission(name='Update Fee Type', code_name='update_fee_type', module_name='Fee Type', module_label='Fee Management', description='User can update Fee Type'),
        Permission(name='Delete Fee Type', code_name='delete_fee_type', module_name='Fee Type', module_label='Fee Management', description='User can delete Fee Type'),

        # ---------- Fee Structure ----------
        Permission(name='Create Fee Structure', code_name='create_fee_structure', module_name='Fee Structure', module_label='Fee Management', description='User can create Fee Structure'),
        Permission(name='Read Fee Structure', code_name='read_fee_structure', module_name='Fee Structure', module_label='Fee Management', description='User can read Fee Structure'),
        Permission(name='Update Fee Structure', code_name='update_fee_structure', module_name='Fee Structure', module_label='Fee Management', description='User can update Fee Structure'),
        Permission(name='Delete Fee Structure', code_name='delete_fee_structure', module_name='Fee Structure', module_label='Fee Management', description='User can delete Fee Structure'),

        # ---------- Fee Invoice ----------
        Permission(name='Create Fee Invoice', code_name='create_fee_invoice', module_name='Fee Invoice', module_label='Fee Management', description='User can create Fee Invoice'),
        Permission(name='Read Fee Invoice', code_name='read_fee_invoice', module_name='Fee Invoice', module_label='Fee Management', description='User can read Fee Invoice'),
        Permission(name='Update Fee Invoice', code_name='update_fee_invoice', module_name='Fee Invoice', module_label='Fee Management', description='User can update Fee Invoice'),
        Permission(name='Delete Fee Invoice', code_name='delete_fee_invoice', module_name='Fee Invoice', module_label='Fee Management', description='User can delete Fee Invoice'),

        # ---------- Fee Invoice Item ----------
        Permission(name='Create Fee Invoice Item', code_name='create_fee_invoice_item', module_name='Fee Invoice Item', module_label='Fee Management', description='User can create Fee Invoice Item'),
        Permission(name='Read Fee Invoice Item', code_name='read_fee_invoice_item', module_name='Fee Invoice Item', module_label='Fee Management', description='User can read Fee Invoice Item'),
        Permission(name='Update Fee Invoice Item', code_name='update_fee_invoice_item', module_name='Fee Invoice Item', module_label='Fee Management', description='User can update Fee Invoice Item'),
        Permission(name='Delete Fee Invoice Item', code_name='delete_fee_invoice_item', module_name='Fee Invoice Item', module_label='Fee Management', description='User can delete Fee Invoice Item'),

        # ---------- Fee Payment ----------
        Permission(name='Create Fee Payment', code_name='create_fee_payment', module_name='Fee Payment', module_label='Fee Management', description='User can create Fee Payment'),
        Permission(name='Read Fee Payment', code_name='read_fee_payment', module_name='Fee Payment', module_label='Fee Management', description='User can read Fee Payment'),
        Permission(name='Update Fee Payment', code_name='update_fee_payment', module_name='Fee Payment', module_label='Fee Management', description='User can update Fee Payment'),
        Permission(name='Delete Fee Payment', code_name='delete_fee_payment', module_name='Fee Payment', module_label='Fee Management', description='User can delete Fee Payment'),

        # ---------- Fee Discount ----------
        Permission(name='Create Fee Discount', code_name='create_fee_discount', module_name='Fee Discount', module_label='Fee Management', description='User can create Fee Discount'),
        Permission(name='Read Fee Discount', code_name='read_fee_discount', module_name='Fee Discount', module_label='Fee Management', description='User can read Fee Discount'),
        Permission(name='Update Fee Discount', code_name='update_fee_discount', module_name='Fee Discount', module_label='Fee Management', description='User can update Fee Discount'),
        Permission(name='Delete Fee Discount', code_name='delete_fee_discount', module_name='Fee Discount', module_label='Fee Management', description='User can delete Fee Discount'),

        # ---------- Student Discount ----------
        Permission(name='Create Student Discount', code_name='create_student_discount', module_name='Student Discount', module_label='Fee Management', description='User can create Student Discount'),
        Permission(name='Read Student Discount', code_name='read_student_discount', module_name='Student Discount', module_label='Fee Management', description='User can read Student Discount'),
        Permission(name='Update Student Discount', code_name='update_student_discount', module_name='Student Discount', module_label='Fee Management', description='User can update Student Discount'),
        Permission(name='Delete Student Discount', code_name='delete_student_discount', module_name='Student Discount', module_label='Fee Management', description='User can delete Student Discount'),

        # ---------- Transport Route ----------
        Permission(name='Create Route', code_name='create_route', module_name='Route', module_label='Transport Management', description='User can create Route'),
        Permission(name='Read Route', code_name='read_route', module_name='Route', module_label='Transport Management', description='User can read Route'),
        Permission(name='Update Route', code_name='update_route', module_name='Route', module_label='Transport Management', description='User can update Route'),
        Permission(name='Delete Route', code_name='delete_route', module_name='Route', module_label='Transport Management', description='User can delete Route'),

        # ---------- Transport Vehicle ----------
        Permission(name='Create Vehicle', code_name='create_vehicle', module_name='Vehicle', module_label='Transport Management', description='User can create Vehicle'),
        Permission(name='Read Vehicle', code_name='read_vehicle', module_name='Vehicle', module_label='Transport Management', description='User can read Vehicle'),
        Permission(name='Update Vehicle', code_name='update_vehicle', module_name='Vehicle', module_label='Transport Management', description='User can update Vehicle'),
        Permission(name='Delete Vehicle', code_name='delete_vehicle', module_name='Vehicle', module_label='Transport Management', description='User can delete Vehicle'),

        # ---------- Transport Allocation ----------
        Permission(name='Create Transport Allocation', code_name='create_transport_allocation', module_name='Transport Allocation', module_label='Transport Management', description='User can create Transport Allocation'),
        Permission(name='Read Transport Allocation', code_name='read_transport_allocation', module_name='Transport Allocation', module_label='Transport Management', description='User can read Transport Allocation'),
        Permission(name='Update Transport Allocation', code_name='update_transport_allocation', module_name='Transport Allocation', module_label='Transport Management', description='User can update Transport Allocation'),
        Permission(name='Delete Transport Allocation', code_name='delete_transport_allocation', module_name='Transport Allocation', module_label='Transport Management', description='User can delete Transport Allocation'),

        # Announcement Permissions
        Permission(name='Create Announcement', code_name='create_announcement', module_name='Announcement', module_label='Communication Management', description='User can create Announcement'),
        Permission(name='Read Announcement', code_name='read_announcement', module_name='Announcement', module_label='Communication Management', description='User can read Announcement'),
        Permission(name='Update Announcement', code_name='update_announcement', module_name='Announcement', module_label='Communication Management', description='User can update Announcement'),
        Permission(name='Delete Announcement', code_name='delete_announcement', module_name='Announcement', module_label='Communication Management', description='User can delete Announcement'),

        # Event Permissions
        Permission(name='Create Event', code_name='create_event', module_name='Event', module_label='Communication Management', description='User can create Event'),
        Permission(name='Read Event', code_name='read_event', module_name='Event', module_label='Communication Management', description='User can read Event'),
        Permission(name='Update Event', code_name='update_event', module_name='Event', module_label='Communication Management', description='User can update Event'),
        Permission(name='Delete Event', code_name='delete_event', module_name='Event', module_label='Communication Management', description='User can delete Event'),

        # Message Permissions
        Permission(name='Create Message', code_name='create_message', module_name='Message', module_label='Communication Management', description='User can create Message'),
        Permission(name='Read Message', code_name='read_message', module_name='Message', module_label='Communication Management', description='User can read Message'),
        Permission(name='Update Message', code_name='update_message', module_name='Message', module_label='Communication Management', description='User can update Message'),
        Permission(name='Delete Message', code_name='delete_message', module_name='Message', module_label='Communication Management', description='User can delete Message'),

        # Notification Permissions
        Permission(name='Create Notification', code_name='create_notification', module_name='Notification', module_label='Communication Management', description='User can create Notification'),
        Permission(name='Read Notification', code_name='read_notification', module_name='Notification', module_label='Communication Management', description='User can read Notification'),
        Permission(name='Update Notification', code_name='update_notification', module_name='Notification', module_label='Communication Management', description='User can update Notification'),
        Permission(name='Delete Notification', code_name='delete_notification', module_name='Notification', module_label='Communication Management', description='User can delete Notification'),

        # Course Permissions
        Permission(name='Create Course', code_name='create_course', module_name='Course', module_label='Course Management', description='User can create Course'),
        Permission(name='Read Course', code_name='read_course', module_name='Course', module_label='Course Management', description='User can read Course'),
        Permission(name='Update Course', code_name='update_course', module_name='Course', module_label='Course Management', description='User can update Course'),
        Permission(name='Delete Course', code_name='delete_course', module_name='Course', module_label='Course Management', description='User can delete Course'),

        # Lesson Permissions
        Permission(name='Create Lesson', code_name='create_lesson', module_name='Lesson', module_label='Course Management', description='User can create Lesson'),
        Permission(name='Read Lesson', code_name='read_lesson', module_name='Lesson', module_label='Course Management', description='User can read Lesson'),
        Permission(name='Update Lesson', code_name='update_lesson', module_name='Lesson', module_label='Course Management', description='User can update Lesson'),
        Permission(name='Delete Lesson', code_name='delete_lesson', module_name='Lesson', module_label='Course Management', description='User can delete Lesson'),

        # CourseEnrollment Permissions
        Permission(name='Create Course Enrollment', code_name='create_course_enrollment', module_name='CourseEnrollment', module_label='Student Management', description='User can create Course Enrollment'),
        Permission(name='Read Course Enrollment', code_name='read_course_enrollment', module_name='CourseEnrollment', module_label='Student Management', description='User can read Course Enrollment'),
        Permission(name='Update Course Enrollment', code_name='update_course_enrollment', module_name='CourseEnrollment', module_label='Student Management', description='User can update Course Enrollment'),
        Permission(name='Delete Course Enrollment', code_name='delete_course_enrollment', module_name='CourseEnrollment', module_label='Student Management', description='User can delete Course Enrollment'),

        # LessonProgress Permissions
        Permission(name='Create Lesson Progress', code_name='create_lesson_progress', module_name='LessonProgress', module_label='Student Management', description='User can create Lesson Progress'),
        Permission(name='Read Lesson Progress', code_name='read_lesson_progress', module_name='LessonProgress', module_label='Student Management', description='User can read Lesson Progress'),
        Permission(name='Update Lesson Progress', code_name='update_lesson_progress', module_name='LessonProgress', module_label='Student Management', description='User can update Lesson Progress'),
        Permission(name='Delete Lesson Progress', code_name='delete_lesson_progress', module_name='LessonProgress', module_label='Student Management', description='User can delete Lesson Progress'),

        # Quiz Permissions
        Permission(name='Create Quiz', code_name='create_quiz', module_name='Quiz', module_label='Assessment Management', description='User can create Quiz'),
        Permission(name='Read Quiz', code_name='read_quiz', module_name='Quiz', module_label='Assessment Management', description='User can read Quiz'),
        Permission(name='Update Quiz', code_name='update_quiz', module_name='Quiz', module_label='Assessment Management', description='User can update Quiz'),
        Permission(name='Delete Quiz', code_name='delete_quiz', module_name='Quiz', module_label='Assessment Management', description='User can delete Quiz'),

        # Question Permissions
        Permission(name='Create Question', code_name='create_question', module_name='Question', module_label='Assessment Management', description='User can create Question'),
        Permission(name='Read Question', code_name='read_question', module_name='Question', module_label='Assessment Management', description='User can read Question'),
        Permission(name='Update Question', code_name='update_question', module_name='Question', module_label='Assessment Management', description='User can update Question'),
        Permission(name='Delete Question', code_name='delete_question', module_name='Question', module_label='Assessment Management', description='User can delete Question'),

        # QuestionOption Permissions
        Permission(name='Create Question Option', code_name='create_question_option', module_name='QuestionOption', module_label='Assessment Management', description='User can create Question Option'),
        Permission(name='Read Question Option', code_name='read_question_option', module_name='QuestionOption', module_label='Assessment Management', description='User can read Question Option'),
        Permission(name='Update Question Option', code_name='update_question_option', module_name='QuestionOption', module_label='Assessment Management', description='User can update Question Option'),
        Permission(name='Delete Question Option', code_name='delete_question_option', module_name='QuestionOption', module_label='Assessment Management', description='User can delete Question Option'),

        # QuizAttempt Permissions
        Permission(name='Create Quiz Attempt', code_name='create_quiz_attempt', module_name='QuizAttempt', module_label='Student Assessment', description='User can create Quiz Attempt'),
        Permission(name='Read Quiz Attempt', code_name='read_quiz_attempt', module_name='QuizAttempt', module_label='Student Assessment', description='User can read Quiz Attempt'),
        Permission(name='Update Quiz Attempt', code_name='update_quiz_attempt', module_name='QuizAttempt', module_label='Student Assessment', description='User can update Quiz Attempt'),
        Permission(name='Delete Quiz Attempt', code_name='delete_quiz_attempt', module_name='QuizAttempt', module_label='Student Assessment', description='User can delete Quiz Attempt'),

        # QuizAnswer Permissions
        Permission(name='Create Quiz Answer', code_name='create_quiz_answer', module_name='QuizAnswer', module_label='Student Assessment', description='User can create Quiz Answer'),
        Permission(name='Read Quiz Answer', code_name='read_quiz_answer', module_name='QuizAnswer', module_label='Student Assessment', description='User can read Quiz Answer'),
        Permission(name='Update Quiz Answer', code_name='update_quiz_answer', module_name='QuizAnswer', module_label='Student Assessment', description='User can update Quiz Answer'),
        Permission(name='Delete Quiz Answer', code_name='delete_quiz_answer', module_name='QuizAnswer', module_label='Student Assessment', description='User can delete Quiz Answer'),

        # Assignment Permissions
        Permission(name='Create Assignment', code_name='create_assignment', module_name='Assignment', module_label='Assignments', description='User can create assignments'),
        Permission(name='Read Assignment', code_name='read_assignment', module_name='Assignment', module_label='Assignments', description='User can read/view assignments'),
        Permission(name='Update Assignment', code_name='update_assignment', module_name='Assignment', module_label='Assignments', description='User can update assignments'),
        Permission(name='Delete Assignment', code_name='delete_assignment', module_name='Assignment', module_label='Assignments', description='User can delete assignments'),

        # AssignmentSubmission Permissions
        Permission(name='Create Submission', code_name='create_submission', module_name='AssignmentSubmission', module_label='Student Submissions', description='User can submit assignments'),
        Permission(name='Read Submission', code_name='read_submission', module_name='AssignmentSubmission', module_label='Student Submissions', description='User can view assignment submissions'),
        Permission(name='Update Submission', code_name='update_submission', module_name='AssignmentSubmission', module_label='Student Submissions', description='User can update assignment submissions'),
        Permission(name='Delete Submission', code_name='delete_submission', module_name='AssignmentSubmission', module_label='Student Submissions', description='User can delete assignment submissions'),
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