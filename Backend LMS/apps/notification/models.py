from django.db import models
from utils.reusable_classes import TimeStamps
from utils.enums import *


class EmailTemplate(TimeStamps):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    alternative_text = models.TextField(blank=True, null=True)
    html_template = models.TextField()
    code_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        # This tells PostgreSQL to use EXACTLY this name
        db_table = 'email_temp'


