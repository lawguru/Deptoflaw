from django.urls import path
from django.views.generic.base import RedirectView
from .views import *

urlpatterns = [
    path('', RedirectView.as_view(url='user/')),
    path('signin/', SignIn.as_view(), name='sign_in'),
    path('profile/', BuildProfile.as_view(), name='build_profile'),
    path('user/', RedirectView.as_view(url='self/')),
    path('user/<pk>/', UpdatePersonalContactInfo.as_view(), name='update_personal_contact_info'),
    path('user/<pk>/change/', ChangeUser.as_view(), name='change_user'),
    path('user/<pk>/phone-numbers/', RedirectView.as_view(url='../#phone-numbers'), name='phone_numbers'),
    path('user/<pk>/emails/', RedirectView.as_view(url='../#emails'), name='emails'),
    path('user/<pk>/addresses/', RedirectView.as_view(url='../#addresses'), name='addresses'),
    path('user/<pk>/links/', RedirectView.as_view(url='../#links'), name='links'),
    path('phonenumber/<user>/add/', AddPhoneNumber.as_view(), name='add_phone_number'),
    path('phonenumber/<int:pk>/delete/', DeletePhoneNumber.as_view(), name='delete_phone_number'),
    path('phonenumber/<int:pk>/setprimary/', SetPrimaryPhoneNumber.as_view(), name='set_primary_phone_number'),
    path('email/<user>/add/', AddEmail.as_view(), name='add_email'),
    path('email/<str:pk>/setprimary/', SetPrimaryEmail.as_view(), name='set_primary_email'),
    path('email/<str:pk>/delete/', DeleteEmail.as_view(), name='delete_email'),
    path('address/<user>/add/', AddAddress.as_view(), name='add_address'),
    path('address/<int:pk>/', RedirectView.as_view(url='change/')),
    path('address/<int:pk>/change/', ChangeAddress.as_view(), name='change_address'),
    path('address/<int:pk>/delete/', DeleteAddress.as_view(), name='delete_address'),
    path('address/<int:pk>/setprimary/', SetPrimaryAddress.as_view(), name='set_primary_address'),
    path('link/<user>/add/', AddLink.as_view(), name='add_link'),
    path('link/<str:pk>/delete/', DeleteLink.as_view(), name='delete_link'),
]