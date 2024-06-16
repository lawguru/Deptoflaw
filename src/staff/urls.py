from django.urls import path
from django.views.generic.base import RedirectView
from .views import *

urlpatterns = [
    path('', RedirectView.as_view(url='../user/list/?role-filter=staff') , name='staffs_list'),
    path('signup/', StaffSignUp.as_view(), name='staff_sign_up'),
    path('signin/', StaffSignIn.as_view(), name='staff_sign_in'),
    path('<int:pk>/', StaffInfo.as_view(), name='staff_info'),
    path('<int:pk>/change/', ChangeStaffProfile.as_view(), name='change_staff_profile'),
    path('<int:pk>/staffprofile/', RedirectView.as_view(url='../#staff-profile'), name='staff_profile'),
]