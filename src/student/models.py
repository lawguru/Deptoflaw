import random
from datetime import datetime
from django.db import models
from django.db.models import Q
from user.models import User
from settings.models import Setting

# Create your models here.


class StudentProfile(models.Model):
    class StudentProfileManager(models.Manager):

        def get_queryset(self):
            current_academic_half = Setting.objects.get(
                key='current_academic_half').value
            return super().get_queryset().annotate(
                academic_half=models.Value(
                    current_academic_half, output_field=models.CharField()),
                course_duration=models.Case(
                    models.When(course='B.Tech', then=4),
                    models.When(course='M.Tech', then=2),
                    models.When(course='PhD', then=6),
                    output_field=models.IntegerField()
                ),
                passed_out=models.ExpressionWrapper(models.Case(
                    models.When(passed_semesters__gte=models.F(
                        'course_duration') * 2, then=True),
                    default=False,
                    output_field=models.BooleanField()
                ), output_field=models.BooleanField()),
                is_current=models.ExpressionWrapper(models.Case(
                    models.When(passed_semesters__lt=models.F(
                        'course_duration') * 2, then=True),
                    default=False,
                    output_field=models.BooleanField()
                ), output_field=models.BooleanField()),
                year=models.Case(
                    models.When(
                        is_current=True,
                        then=datetime.now().year - models.F('registration_year')),
                    default=0,
                    output_field=models.IntegerField()
                ),
                semester=models.Case(
                    models.When(
                        academic_half='odd',
                        then=models.F('year') * 2 - 1),
                    default=models.F('year') * 2,
                    output_field=models.IntegerField()
                ),
                roll=models.Case(
                    models.When(
                        is_current=True,
                        then=models.ExpressionWrapper(models.functions.Concat(models.F('semester'), datetime.now(
                        ).year % 100, models.F('registration_year') % 100), output_field=models.CharField())
                    ),
                    default=models.Value(
                        'SSYYRR', output_field=models.CharField()),
                    output_field=models.CharField()
                )
            )

    objects = StudentProfileManager()

    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        base_manager_name = 'objects'

    course_choices = [
        ('B.Tech', 'Bachelor of Technology'),
        ('M.Tech', 'Master of Technology'),
        ('PhD', 'Doctor of Philosophy')
    ]

    class CurrentStudentProfile(models.Manager):
        def get_queryset(self):
            q = super().get_queryset()
            q_ids = [o.id for o in q if o.is_current]
            q = q.filter(id__in=q_ids)
            return q

    class PassedOutStudentProfile(models.Manager):
        def get_queryset(self):
            q = super().get_queryset()
            q_ids = [o.id for o in q if o.passed_out]
            q = q.filter(id__in=q_ids)
            return q

    class DroppedOutStudentProfile(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(dropped_out=True)

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='student_profile')
    registration_number = models.PositiveBigIntegerField(
        unique=True, help_text='YYYYXXXXXXX', validators=[models.validators.MinValueValidator(20000000001), models.validators.MaxValueValidator(99999999999)])
    course = models.CharField(max_length=6, choices=course_choices)
    number = models.PositiveBigIntegerField(
        help_text='10 digit number from Exam Roll no.', validators=[models.validators.MinValueValidator(1000000000), models.validators.MaxValueValidator(9999999999)])
    id_number = models.PositiveSmallIntegerField('ID Number',
                                                 help_text='Number at the end of ID Card', validators=[models.validators.MinValueValidator(1), models.validators.MaxValueValidator(999)])
    dropped_out = models.BooleanField(default=False)
    is_cr = models.BooleanField(default=False)

    id_card = models.CharField(
        max_length=15, editable=False, default='YYCSEXXXXX')
    registration_year = models.PositiveIntegerField(
        editable=False, default=2000)
    backlog_count = models.PositiveSmallIntegerField(editable=False, default=0)
    pass_out_year = models.PositiveIntegerField(
        editable=False, null=True, blank=True, default=None)
    passed_semesters = models.PositiveSmallIntegerField(
        editable=False, default=0)
    cgpa = models.FloatField(editable=False, default=0)

    @property
    def edit_users(self):
        if self.user.is_superuser:
            return User.objects.filter(pk=self.user.pk)
        return User.objects.filter(Q(Q(is_superuser=True) | Q(pk=self.user.pk))).distinct()

    @property
    def view_users(self):
        if self.user.is_superuser or self.user.is_coordinator or self.is_cr:
            return User.objects.all()
        # To be able to access annotations in the default manager's get_queryset
        self_annotated = StudentProfile.objects.get(pk=self.pk)
        return User.objects.filter(
            Q(
                Q(is_superuser=True) | Q(is_coordinator=True) | Q(pk=self.pk) |
                Q(
                    Q(student_profile__year=self_annotated.year) & Q(
                        student_profile__course=self.course) & Q(student_profile__is_cr=True)
                ) |
                Q(
                    Q(student_profile__registration_year=self.registration_year) & Q(
                        student_profile__course=self.course) & Q(student_profile__is_cr=True)
                ) |
                Q(
                    Q(student_profile__pass_out_year=self.pass_out_year) & Q(
                        student_profile__course=self.course) & Q(student_profile__is_cr=True)
                )
            )
        ).distinct()

    @property
    def make_cr_users(self):
        if self.user.is_cr:
            return User.objects.none()
        self_annotated = StudentProfile.objects.get(pk=self.pk)
        return User.objects.filter(
            Q(
                Q(is_superuser=True) | Q(is_coordinator=True) |
                Q(
                    Q(student_profile__year=self_annotated.year) & Q(
                        student_profile__course=self.course) & Q(student_profile__is_cr=True)
                )
            )
        ).distinct()

    @property
    def remove_cr_users(self):
        return User.objects.filter(
            Q(Q(is_superuser=True) | Q(is_coordinator=True) | Q(pk=self.pk))
        )

    @property
    def year_suffix(self):
        return 'st' if self.year == 1 else 'nd' if self.year == 2 else 'rd' if self.year == 3 else 'th'

    @property
    def year_name(self):
        if self.year in range(1, 8):
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
        return f'{self.year}th'

    @property
    def semester_suffix(self):
        return 'st' if self.semester == 1 else 'nd' if self.semester == 2 else 'rd' if self.semester == 3 else 'th'

    @property
    def semester_name(self):
        if self.semester in range(1, 8):
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
        return f'{self.semester}th'

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
        if self.pk and StudentProfile.objects.filter(pk=self.pk).exists():
            self.cgpa = self.calculate_cgpa()
            self.backlog_count = sum(
                [semester_report_card.backlogs for semester_report_card in self.semester_report_cards.all()])
            self.passed_semesters = sum(
                [1 for semester_report_card in self.semester_report_cards.all() if semester_report_card.passed])
            if StudentProfile.objects.get(pk=self.pk).backlog_count > 0:
                if self.backlog_count == 0 and not self.is_current and not self.dropped_out:
                    self.pass_out_year = datetime.now().year
                else:
                    self.pass_out_year = None
            while self.semester_report_cards.count() < self.semester:
                SemesterReportCard.objects.create(student_profile=self)
        if self.is_cr:
            self.user.is_approved = True
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
    class SemesterReportCardManager(models.Manager):

        def get_queryset(self):
            return super().get_queryset().annotate(
                semester=models.Window(
                    expression=models.functions.RowNumber()),
                roll=models.ExpressionWrapper(models.functions.Concat(models.F('semester'), datetime.now(
                ).year % 100, models.F('student_profile__registration_year') % 100), output_field=models.CharField()),
            )

    objects = SemesterReportCardManager()

    student_profile = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name='semester_report_cards')
    subjects = models.JSONField(default=list, blank=True, null=True)
    subject_codes = models.JSONField(default=list, blank=True, null=True)
    subject_credits = models.JSONField(default=list, blank=True, null=True)
    subject_letter_grades = models.JSONField(
        default=list, blank=True, null=True)
    subject_passing_grade_points = models.JSONField(
        default=list, blank=True, null=True)
    subject_grade_points = models.JSONField(
        default=list, blank=True, null=True)
    backlogs = models.PositiveSmallIntegerField(default=0)
    passed = models.BooleanField(default=False)
    total_credits = models.FloatField(default=0)
    earned_credits = models.FloatField(default=0)
    sgpa = models.FloatField(default=0)
    is_complete = models.BooleanField(default=False)

    @property
    def edit_users(self):
        if self.student_profile.user.is_superuser:
            return User.objects.filter(pk=self.user.pk)
        return User.objects.filter(Q(Q(is_superuser=True) | Q(pk=self.student_profile.user.pk))).distinct()

    def get_sgpa(self):
        sgpa = 0
        for i in range(len(self.subjects)):
            if self.subject_letter_grades[i] == 'F':
                sgpa = sgpa + \
                    float(self.subject_credits[i]) * \
                    float(self.subject_passing_grade_points[i])
            else:
                sgpa = sgpa + \
                    float(self.subject_credits[i]) * \
                    float(self.subject_grade_points[i])
        return (sgpa / self.total_credits) if self.total_credits > 0 else 0

    def semester(self):
        try:
            return list(self.student_profile.semester_report_cards.all()).index(self) + 1
        except:
            return self.student_profile.semester_report_cards.count() + 1

    def save(self, *args, **kwargs):
        if self.pk:
            self.backlogs = self.subject_letter_grades.count('F')
            self.passed = True if 'F' not in self.subject_letter_grades else False
            self.earned_credits = round(sum([(float(tuple[0]) * float(tuple[1]) / 10)
                                        for tuple in list(zip(self.subject_credits, self.subject_grade_points))]), 2)
        elif SemesterReportCardTemplate.objects.filter(course=self.student_profile.course, semester=self.semester()).exists():
            template = SemesterReportCardTemplate.objects.get(
                course=self.student_profile.course, semester=self.semester())
            self.subjects = template.subjects
            self.subject_codes = template.subject_codes
            self.subject_credits = template.subject_credits
            self.subject_passing_grade_points = template.subject_passing_grade_points
            self.subject_letter_grades = ['S' for _ in template.subjects]
            self.subject_grade_points = [0 for _ in template.subjects]

        self.total_credits = round(
            sum([float(subject_credit) for subject_credit in self.subject_credits]), 1)

        if self.pk:
            self.sgpa = round(self.get_sgpa(), 2)

        super().save(*args, **kwargs)

        if self.pk:
            self.student_profile.save()


class SemesterReportCardTemplate(models.Model):
    course = models.CharField(
        max_length=6, choices=StudentProfile.course_choices)
    semester = models.PositiveSmallIntegerField()
    subjects = models.JSONField(default=list, blank=True, null=True)
    subject_codes = models.JSONField(default=list, blank=True, null=True)
    subject_credits = models.JSONField(default=list, blank=True, null=True)
    subject_passing_grade_points = models.JSONField(
        default=list, blank=True, null=True)

    @property
    def view_users(self):
        return User.objects.all()

    @property
    def edit_users(self):
        return User.objects.filter(
            Q(is_superuser=True) | Q(is_coordinator=True) |
            Q(
                Q(student_profile__is_cr=True)
                & Q(student_profile__course=self.course)
                # & Q(student_profile__semester=self.semester)
            )
        )

    class Meta:
        unique_together = [['course', 'semester']]
