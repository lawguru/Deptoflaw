import random
from datetime import datetime
from django.db import models
from user.models import User
from settings.models import Setting

# Create your models here.


class StudentProfile(models.Model):
    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'

    course_choices = [
        ('B.Tech', 'Bachelor of Technology'),
        ('M.Tech', 'Master of Technology'),
        ('PhD', 'Doctor of Philosophy')
    ]

    class CurrentStudentProfile(models.Manager):
        def get_queryset(self):
            q=super().get_queryset()
            q_ids = [o.id for o in q if o.is_current]
            q = q.filter(id__in=q_ids)
            return q

    class PassedOutStudentProfile(models.Manager):
        def get_queryset(self):
            q=super().get_queryset()
            q_ids = [o.id for o in q if o.passed_out]
            q = q.filter(id__in=q_ids)
            return q

    class DroppedOutStudentProfile(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(dropped_out=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    registration_number = models.PositiveBigIntegerField(
        unique=True, help_text='20YYXXXXXXX')
    course = models.CharField(max_length=6, choices=course_choices)
    number = models.PositiveBigIntegerField(
        help_text='10 digit number from Exam Roll no.', default=0)
    id_number = models.PositiveSmallIntegerField('ID Number',
        help_text='Number at the end of ID Card', default=0)
    dropped_out = models.BooleanField(default=False)

    id_card = models.CharField(max_length=15, editable=False, default='YYCSEXXXXX')
    registration_year = models.PositiveIntegerField(editable=False, default=2000)
    backlog_count = models.PositiveSmallIntegerField(editable=False, default=0)
    pass_out_year = models.PositiveIntegerField(editable=False, null=True, blank=True, default=None)
    passed_semesters = models.PositiveSmallIntegerField(editable=False, default=0)
    cgpa = models.FloatField(editable=False, default=0)

    @property
    def course_duration(self):
        return {'B.Tech': 4, 'M.Tech': 2, 'PhD': 6}[self.course]

    @property
    def year(self):
        year = int(Setting.objects.get(key='current_academic_year').value) - self.registration_year + 1
        return 1 if year <= 0 else year if year <= self.course_duration else self.course_duration

    @property
    def semester(self):
        return self.year * 2 - 1 if Setting.objects.get( key='current_academic_half') == 'odd' else self.year * 2

    @property
    def roll(self):
        return f'{self.semester:02d}{datetime.now().year % 100}{self.registration_year % 100}'
    

    @property
    def passed_out(self):
        return self.passed_semesters >= (self.course_duration * 2) and not self.dropped_out

    @property
    def is_current(self):
        return self.passed_semesters < (self.course_duration * 2) and not self.dropped_out


    @property
    def year_suffix(self):
        return 'st' if self.year == 1 else 'nd' if self.year == 2 else 'rd' if self.year == 3 else 'th'

    @property
    def year_name(self):
        return {
            1: 'First',
            2: 'Second',
            3: 'Third',
            4: 'Fourth',
            5: 'Fifth',
            6: 'Sixth',
            7: 'Seventh',
            8: 'Eighth',
        }[self.year]

    @property
    def semester_suffix(self):
        return 'st' if self.semester == 1 else 'nd' if self.semester == 2 else 'rd' if self.semester == 3 else 'th'

    @property
    def semester_name(self):
        return {
            1: 'First',
            2: 'Second',
            3: 'Third',
            4: 'Fourth',
            5: 'Fifth',
            6: 'Sixth',
            7: 'Seventh',
            8: 'Eighth',
        }[self.semester]

    def calculate_cgpa(self):
        cgpa = 0
        total_credits = 0
        for semester_report_card in self.semester_report_cards.all():
            cgpa = cgpa + semester_report_card.sgpa * semester_report_card.total_credits
            total_credits = total_credits + semester_report_card.total_credits
        return (cgpa / total_credits) if total_credits > 0 else 0

    def save(self, *args, **kwargs):
        self.registration_year = int(f'{self.registration_number}'[:4])
        self.id_card = f'{self.registration_year % 100}CSE{"BTC" if self.course == "B.Tech" else "MTC" if self.course == "M.Tech" else "PHD"}{self.id_number:03d}'
        self.backlog_count = sum([semester_report_card.backlogs for semester_report_card in self.semester_report_cards.all()])
        self.passed_semesters = sum([1 for semester_report_card in self.semester_report_cards.all() if semester_report_card.passed])
        self.cgpa = self.calculate_cgpa()
        if self.pk and StudentProfile.objects.filter(pk=self.pk).exists():
            if StudentProfile.objects.get(pk=self.pk).backlog_count > 0:
                if self.backlog_count == 0 and not self.is_current and not self.dropped_out:
                    self.pass_out_year = datetime.now().year
                else:
                    self.pass_out_year = None
        if not self.pk and not hasattr(self, 'user'):
            self.user = User.objects.create(role='student')
        if self.pk:
            while self.semester_report_cards.count() < self.semester:
                SemesterReportCard.objects.create(student_profile=self)
        super().save(*args, **kwargs)
        self.user.save()

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' (' + self.roll + ')'


class CurrentStudentProfile(StudentProfile):
    objects = StudentProfile.CurrentStudentProfile()

    class Meta:
        proxy = True
        verbose_name = 'Current Student'
        verbose_name_plural = 'Current Students'


class PassedOutStudentProfile(StudentProfile):
    objects = StudentProfile.PassedOutStudentProfile()

    class Meta:
        proxy = True
        verbose_name = 'Pass Out Student'
        verbose_name_plural = 'Pass Out Students'


class DroppedOutStudentProfile(StudentProfile):
    objects = StudentProfile.DroppedOutStudentProfile()

    class Meta:
        proxy = True
        verbose_name = 'Drop Out Student'
        verbose_name_plural = 'Drop Out Students'


class SemesterReportCard(models.Model):
    student_profile = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='semester_report_cards')
    subjects = models.JSONField(default=list, blank=True, null=True)
    subject_codes = models.JSONField(default=list, blank=True, null=True)
    subject_credits = models.JSONField(default=list, blank=True, null=True)
    subject_letter_grades = models.JSONField(default=list, blank=True, null=True)
    subject_passing_grade_points = models.JSONField(default=list, blank=True, null=True)
    subject_grade_points = models.JSONField(default=list, blank=True, null=True)
    backlogs = models.PositiveSmallIntegerField(default=0)
    passed = models.BooleanField(default=False)
    total_credits = models.FloatField(default=0)
    earned_credits = models.FloatField(default=0)
    sgpa = models.FloatField(default=0)
    is_complete = models.BooleanField(default=False)

    def get_sgpa(self):
        sgpa = 0
        for i in range(len(self.subjects)):
            if self.subject_letter_grades[i] == 'F':
                sgpa = sgpa + float(self.subject_credits[i]) * float(self.subject_passing_grade_points[i])
            else:
                sgpa = sgpa + float(self.subject_credits[i]) * float(self.subject_grade_points[i])
        return (sgpa / self.total_credits) if self.total_credits > 0 else 0
    
    def save(self, *args, **kwargs):
        self.backlogs = self.subject_letter_grades.count('F')
        self.passed = True if 'F' not in self.subject_letter_grades else False
        self.total_credits = round(sum([float(subject_credit) for subject_credit in self.subject_credits]), 1)
        self.earned_credits = round(sum([(float(tuple[0]) * float(tuple[1]) / 10) for tuple in list(zip(self.subject_credits, self.subject_grade_points))]), 2)
        self.sgpa = round(self.get_sgpa(), 2)
        self.student_profile.save()
        super().save(*args, **kwargs)