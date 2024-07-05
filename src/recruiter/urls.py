from django.urls import path
from django.views.generic.base import RedirectView
from .views import *

urlpatterns = [
    path('', RedirectView.as_view(url='../user/list/?role-filter=recruiter') , name='recruiters_list'),
    path('signup/', RecruiterSignUp.as_view(), name='recruiter_sign_up'),
    path('signin/', RecruiterSignIn.as_view(), name='recruiter_sign_in'),
    path('<int:pk>/', RecruiterInfo.as_view(), name='recruiter_info'),
    path('<int:pk>/change/', ChangeRecruiterProfile.as_view(), name='change_recruiter_profile'),
    path('<int:pk>/recruiterprofile/', RedirectView.as_view(url='../#recruiter-profile'), name='recruiter_profile'),
]