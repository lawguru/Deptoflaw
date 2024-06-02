from django.contrib import admin
from .models import CurrentStudentProfile, DroppedOutStudentProfile, PassedOutStudentProfile

# Register your models here.


class StudentProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__full_name', 'registration_number',
                     'course', 'registration_year']
    readonly_fields = ['registration_year', 'pass_out_year']
    fieldsets = [
        (
            None,
            {
                'fields': ['user', ('id_card', 'id_number'), 'course', ('registration_number', 'registration_year'), ('passed_out', 'is_current')],
            }
        ),
    ]

    @admin.display(ordering='user__full_name', description='Name')
    def user__full_name(self, obj):
        return obj.user.full_name


@admin.register(CurrentStudentProfile)
class CurrentStudentProfileAdmin(StudentProfileAdmin):
    list_display = ['user__full_name', 'registration_number',
                    'course', 'registration_year']
    list_filter = ['course']
    fieldsets = [
        (
            None,
            {
                'fields': ['user', ('id_number'), 'course', ('registration_number', 'registration_year')],
            }
        ),
    ]


@admin.register(PassedOutStudentProfile)
class CurrentStudentProfileAdmin(StudentProfileAdmin):
    list_display = ['user__full_name', 'registration_number',
                    'course', 'registration_year']
    list_filter = ['course']
    fieldsets = [
        (
            None,
            {
                'fields': ['user', ('id_number'), 'course', ('registration_number', 'registration_year'), 'pass_out_year'],
            }
        ),
    ]


@admin.register(DroppedOutStudentProfile)
class CurrentStudentProfileAdmin(StudentProfileAdmin):
    list_display = ['user__full_name', 'registration_number',
                    'course', 'registration_year']
    list_filter = ['course']
    fieldsets = [
        (
            None,
            {
                'fields': ['user', ('id_number'), 'course', ('registration_number', 'registration_year')],
            }
        ),
    ]
