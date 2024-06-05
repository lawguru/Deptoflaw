from django.contrib import admin
from .models import User, PhoneNumber, Email
from student.models import StudentProfile
from resume.models import OtherEducation
from staff.models import StaffProfile

# Register your models here.


class PhoneNumberInlineAdmin(admin.TabularInline):
    model = PhoneNumber
    min_num = 0
    extra = 0


class EmailInlineAdmin(admin.TabularInline):
    model = Email
    min_num = 0
    extra = 0


class StudentProfileInlineAdmin(admin.TabularInline):
    model = StudentProfile
    min_num = 0
    extra = 0


class OtherEducationInlineAdmin(admin.TabularInline):
    model = OtherEducation
    min_num = 0
    extra = 0


class StaffProfileInlineAdmin(admin.TabularInline):
    model = StaffProfile
    min_num = 0
    max_num = 1
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'is_coordinator', 'is_staff', 'is_superuser')
    readonly_fields = ('last_login', 'date_joined')
    inlines = [PhoneNumberInlineAdmin, EmailInlineAdmin,
               StudentProfileInlineAdmin, OtherEducationInlineAdmin, StaffProfileInlineAdmin]
    fieldsets = [
        (
            'Personal Information',
            {
                'fields': [('first_name', 'last_name'), ('last_login', 'date_joined'), 'bio'],
            }
        ),
        (
            'Permissions',
            {
                'fields': [('is_staff', 'is_superuser')],
            }
        ),
        (
            'Groups and Permissions',
            {
                'classes': ['collapse'],
                'fields': [('groups', 'user_permissions')],
            }
        )
    ]
