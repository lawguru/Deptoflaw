from django.contrib import admin
from .models import StudentProfile
# Register your models here.

@admin.register(StudentProfile)
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