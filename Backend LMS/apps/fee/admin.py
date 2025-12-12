from django.contrib import admin

from apps.fee.models import FeeInvoice

# Register your models here.

# admin.py
@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'student', 'academic_year', 'total_amount', 'due_amount', 'status', 'due_date']
    list_filter = ['status', 'academic_year', 'year']
    search_fields = ['invoice_number', 'student__user__first_name', 'student__user__last_name']
    readonly_fields = ['invoice_number', 'created_at', 'updated_at']  # Invoice number is read-only
    ordering = ['-created_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['student', 'academic_year']
        return self.readonly_fields