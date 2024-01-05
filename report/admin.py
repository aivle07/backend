from django.contrib import admin
from report.models import Report
# Register your models here.

@admin.register(Report)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'file', 'create_dt')
    
