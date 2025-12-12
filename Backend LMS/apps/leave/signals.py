# signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import LeaveApplication, LeaveHistory
from utils.enums import PENDING, APPROVED, REJECTED, CANCELLED

# Store old instance data before save
_leave_application_old_data = {}

@receiver(pre_save, sender=LeaveApplication)
def store_old_leave_application(sender, instance, **kwargs):
    """Store old data before save for comparison"""
    if instance.pk:  # Only for updates, not new records
        try:
            old_instance = LeaveApplication.objects.get(pk=instance.pk)
            _leave_application_old_data[instance.pk] = {
                'status': old_instance.status,
                'start_date': old_instance.start_date,
                'end_date': old_instance.end_date,
                'total_days': old_instance.total_days,
                'reason': old_instance.reason,
            }
        except LeaveApplication.DoesNotExist:
            pass


@receiver(post_save, sender=LeaveApplication)
def create_leave_history(sender, instance, created, **kwargs):
    """Automatically create history entry when leave application is created or updated"""
    
    # Skip if this is a history record being saved (prevent recursion)
    if kwargs.get('raw', False):
        return
    
    if created:
        # New leave application created
        LeaveHistory.objects.create(
            leave_application=instance,
            action='created',
            changed_by=instance.created_by if hasattr(instance, 'created_by') else None,
            new_status=instance.status,
            changes={
                'leave_type': instance.leave_type.name if instance.leave_type else None,
                'start_date': str(instance.start_date),
                'end_date': str(instance.end_date),
                'total_days': instance.total_days,
                'reason': instance.reason
            }
        )
    else:
        # Leave application updated
        old_data = _leave_application_old_data.get(instance.pk)
        
        if old_data:
            # Track what changed
            changes = {}
            
            if old_data['status'] != instance.status:
                changes['status'] = {
                    'from': old_data['status'],
                    'to': instance.status
                }
            
            if old_data['start_date'] != instance.start_date:
                changes['start_date'] = {
                    'from': str(old_data['start_date']),
                    'to': str(instance.start_date)
                }
            
            if old_data['end_date'] != instance.end_date:
                changes['end_date'] = {
                    'from': str(old_data['end_date']),
                    'to': str(instance.end_date)
                }
            
            if old_data['total_days'] != instance.total_days:
                changes['total_days'] = {
                    'from': old_data['total_days'],
                    'to': instance.total_days
                }
            
            if old_data['reason'] != instance.reason:
                changes['reason_updated'] = True
            
            # Determine action based on status change
            action = 'modified'
            if old_data['status'] != instance.status:
                if instance.status == APPROVED:
                    action = 'approved'
                elif instance.status == REJECTED:
                    action = 'rejected'
                elif instance.status == CANCELLED:
                    action = 'cancelled'
            
            # Only create history if something actually changed
            if changes:
                LeaveHistory.objects.create(
                    leave_application=instance,
                    action=action,
                    changed_by=instance.updated_by if hasattr(instance, 'updated_by') else None,
                    previous_status=old_data['status'],
                    new_status=instance.status,
                    changes=changes
                )
            
            # Clean up stored data
            _leave_application_old_data.pop(instance.pk, None)