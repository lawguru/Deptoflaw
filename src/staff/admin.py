from django.contrib import admin
from .models import StaffProfile

# Register your models here.
@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
  list_display = ("user__full_name", "id_number", "designation", "qualification")
  list_filter = ('designation', 'qualification')

  fieldsets = [
    (
      None,
      {
        'fields': ['user', 'id_number', ('designation', 'qualification'), ('is_hod', 'is_tpc_head')],
      }
    ),
  ]

  @admin.display(ordering='user__full_name', description='Name')
  def user__full_name(self, obj):
    return obj.user.get_full_name()