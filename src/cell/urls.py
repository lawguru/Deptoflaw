from django.urls import path
from .views import index, contact, notices, add_notice

urlpatterns = [
    path('', index, name='index'),
    path('contact/', contact, name='contact'),
    path('notice/', notices, name='notices'),
    path('notice/add/', add_notice, name='add_notice'),
]