from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('contact/', contact, name='contact'),
    path('notice/', notices, name='notices'),
    path('notice/add/', add_notice, name='add_notice'),
    path('<int:user>/recruitmentpost/', ListRecruitmentPost.as_view(), name='recruitment_posts'),
    path('<int:user>/recruitmentpost/add/', AddRecruitmentPost.as_view(), name='add_recruitment_post'),
    path('recruitmentpost/<int:pk>/', ViewRecruitmentPost.as_view(), name='view_recruitment_post'),
    path('recruitmentpost/<int:pk>/shareupdate/', AddRecruitmentPostUpdate.as_view(), name='add_recruitment_post_update'),
    path('recruitmentpost/<int:pk>/change/', ChangeRecruitmentPost.as_view(), name='change_recruitment_post'),
    path('recruitmentpost/<int:pk>/activate/', ActivateRecruitmentPost.as_view(), name='activate_recruitment_post'),
    path('recruitmentpost/<int:pk>/deactivate/', DeactivateRecruitmentPost.as_view(), name='deactivate_recruitment_post'),
]