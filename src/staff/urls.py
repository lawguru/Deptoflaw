from django.urls import path
from django.views.generic.base import RedirectView
from .views import *

urlpatterns = [
    path('', StaffListView.as_view() , name='staffs_list'),
    path('<int:pk>/', StaffProfileDetail.as_view(), name='staff_profile'), 
    path('<int:pk>/change/', ChangeStaffProfile.as_view(), name='change_staff_profile'),
    path('signup/', StaffSignUp.as_view(), name='staff_sign_up'),
    path('signin/', StaffSignIn.as_view(), name='staff_sign_in'),
    path('updatestaffinfo/<int:pk>/', UpdateStaffInfo.as_view(), name='update_staff_info'),
    path('updatestaffinfo/<int:pk>/staffprofile/', RedirectView.as_view(url='../#staff-profile'), name='staff_profile'),
]