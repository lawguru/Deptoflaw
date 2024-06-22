from django.urls import path
from .views import *

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('contact/', Contact.as_view(), name='contact'),
    path('notices/', ListNotice.as_view(), name='notices'),
    path('notices/add/', AddNotice.as_view(), name='add_notice'),
    path('notices/<int:pk>/change/', ChangeNotice.as_view(), name='change_notice'),
    path('recruitmentpost/', ListRecruitmentPost.as_view(), name='recruitment_posts'),
    path('recruitmentpost/add/', AddRecruitmentPost.as_view(), name='add_recruitment_post'),
    path('recruitmentpost/<int:pk>/', ViewRecruitmentPost.as_view(), name='view_recruitment_post'),
    path('recruitmentpost/<int:pk>/skill/', AddRecruitmentSkill.as_view(), name='add_recruitment_post_skill'),
    path('recruitmentpost/<int:pk>/skill/<int:skill>/', DeleteRecruitmentSkill.as_view(), name='delete_recruitment_post_skill'),
    path('recruitmentpost/<int:pk>/change/', ChangeRecruitmentPost.as_view(), name='change_recruitment_post'),
    path('recruitmentpost/<int:pk>/apply/', AddRecruitmentApplication.as_view(), name='apply_recruitment_post'),
    path('recruitmentpost/<int:pk>/shareupdate/', AddRecruitmentPostUpdate.as_view(), name='add_recruitment_post_update'),
    path('recruitmentpost/<int:pk>/applications/', RecruitmentApplications.as_view(), name='recruitment_applications'),
    path('recruitmentpost/<int:pk>/applications/csv/', RecruitmentApplicationsCSV.as_view(), name='recruitment_applications_csv'),
    path('recruitmentpost/<int:pk>/skillautocomplete/', SkillAutocomplete.as_view(), name='recruitment_post_skill_autocomplete'),
    path('recruitmentpostupdate/<int:pk>/change/', ChangeRecruitmentPostUpdate.as_view(), name='change_recruitment_post_update'),
    path('recruitmentapplication/<int:pk>/select/', SelectRecruitmentApplication.as_view(), name='select_recruitment_application'),
    path('recruitmentapplication/<int:pk>/reject/', RejectRecruitmentApplication.as_view(), name='reject_recruitment_application'),
    path('recruitmentapplication/<int:pk>/shortlist/', ShortlistRecruitmentApplication.as_view(), name='shortlist_recruitment_application'),
    path('recruitmentapplication/<int:pk>/pending/', PendingRecruitmentApplication.as_view(), name='pending_recruitment_application'), 
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
]