from django.urls import path
from django.views.generic.base import RedirectView
from .views import *

urlpatterns = [
    path('', StudentListView.as_view() , name='students_list'),
    path('<int:pk>/', StudentProfileDetail.as_view(), name='student_profile'),
    path('<int:pk>/change/', ChangeStudentProfile.as_view(), name='change_student_profile'),
    path('signup/', StudentSignUp.as_view(), name='student_sign_up'),
    path('signin/', StudentSignIn.as_view(), name='student_sign_in'),
    path('updateacademicinfo/<int:pk>/', UpdateAcademicInfo.as_view(), name='update_academic_info'),
    path('updateacademicinfo/<int:pk>/studentprofile/', RedirectView.as_view(url='../#student-profile'), name='student_profile'),
    path('semesterreportcard/<int:profile>/<int:sem>/change/', ChangeSemesterReportCard.as_view(), name='change_semester_report_card'),
]