from django.contrib import admin
from .models import Notice, Message, Quote

# Register your models here.
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'added_by')
    search_fields = ('title', 'description', 'added_by__full_name')
    readonly_fields = ('date', 'date_edited')

    fieldsets = [
        (
            None,
            {
                'fields': ['title', 'description', ('date', 'date_edited'), 'added_by'],
            }
        ),
    ]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'sender_designation', 'sender_company', 'message')
    search_fields = ('sender', 'sender_email', 'sender_phone', 'message', 'sender_designation', 'sender_company')
    readonly_fields = ('date', 'date_edited')

    fieldsets = [
        (
            None,
            {
                'fields': ['sender', ('sender_designation', 'sender_company'), ('sender_phone', 'sender_email'), ('date', 'date_edited'), 'message'],
            }
        ),
    ]

admin.site.register(Quote)