from django.urls import path
from django.views.generic.base import RedirectView
from .views import *

urlpatterns = [
    path('', RecruiterListView.as_view() , name='recruiters_list'),
    path('<int:pk>/', RecruiterProfileDetail.as_view(), name='recruiter_profile'), 
    path('<int:pk>/change/', ChangeRecruiterProfile.as_view(), name='change_recruiter_profile'),
    path('signup/', RecruiterSignUp.as_view(), name='recruiter_sign_up'),
    path('signin/', RecruiterSignIn.as_view(), name='recruiter_sign_in'),
    path('updaterecruiterinfo/<int:pk>/', UpdateRecruiterInfo.as_view(), name='update_recruiter_info'),
    path('updaterecruiterinfo/<int:pk>/recruiterprofile/', RedirectView.as_view(url='../#recruiter-profile'), name='recruiter_profile'),
]