from django.urls import path
from django.views.generic.base import RedirectView
from .views import *

urlpatterns = [
    path('', RedirectView.as_view(url='self/')),
    path('self/', SelfUser.as_view(), name='self_user'),
    path('signin/', SignIn.as_view(), name='sign_in'),
    path('<int:pk>/', BuildProfile.as_view(), name='build_profile'),
    path('<int:pk>/personal/', PersonalContactInfo.as_view(), name='personal_contact_info'),
    path('<int:pk>/personal/phone-numbers/', RedirectView.as_view(url='../#phone-numbers'), name='phone_numbers'),
    path('<int:pk>/personal/emails/', RedirectView.as_view(url='../#emails'), name='emails'),
    path('<int:pk>/personal/addresses/', RedirectView.as_view(url='../#addresses'), name='addresses'),
    path('<int:pk>/personal/links/', RedirectView.as_view(url='../#links'), name='links'),
    path('<int:pk>/change/', ChangeUser.as_view(), name='change_user'),
    path('<int:pk>/setprimaryphonenumber/<int:phone_number>/', SetPrimaryPhoneNumber.as_view(), name='set_primary_phone_number'),
    path('<int:pk>/setprimaryemail/<str:email>/', SetPrimaryEmail.as_view(), name='set_primary_email'),
    path('<int:pk>/setprimaryaddress/<int:address>/', SetPrimaryAddress.as_view(), name='set_primary_address'),
    path('phonenumber/add/', AddPhoneNumber.as_view(), name='add_phone_number'),
    path('phonenumber/<int:pk>/delete/', DeletePhoneNumber.as_view(), name='delete_phone_number'),
    path('email/add/', AddEmail.as_view(), name='add_email'),
    path('email/<str:pk>/delete/', DeleteEmail.as_view(), name='delete_email'),
    path('address/add/', AddAddress.as_view(), name='add_address'),
    path('address/<int:pk>/', RedirectView.as_view(url='change/')),
    path('address/<int:pk>/change/', ChangeAddress.as_view(), name='change_address'),
    path('address/<int:pk>/delete/', DeleteAddress.as_view(), name='delete_address'),
    path('link/add/', AddLink.as_view(), name='add_link'),
    path('link/<str:pk>/delete/', DeleteLink.as_view(), name='delete_link'),
]