from django.db import models
from django.db.models.functions import Lower
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import timedelta, datetime
from user.models import User
from resume.models import Skill
from django.db.models import OuterRef, Subquery, Func
from django.db.models import Q

# Create your models here.


class Notice(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user):
            if user.is_superuser or user.is_coordinator or (user.role == 'staff' and user.is_approved):
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    kind_choices = [
        ('N', 'Notice'),
        ('U', 'Update'),
    ]

    kind = models.CharField(max_length=1, choices=kind_choices, default='N', editable=False)
    title = models.CharField(max_length=150)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True, editable=False)
    date_edited = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(
        'user.User', null=True, on_delete=models.SET_NULL, related_name='notices')

    @cached_property
    def edit_users(self):
        return User.objects.filter(is_superuser=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    sender = models.CharField(max_length=150)
    sender_designation = models.CharField(max_length=150)
    sender_company = models.CharField(max_length=150)
    sender_phone = models.CharField(max_length=150)
    sender_email = models.EmailField()
    message = models.TextField()
    handled = models.BooleanField(default=False)
    handled_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='handled_messages')
    handled_on = models.DateTimeField(null=True, blank=True, editable=False)
    handled_notes = models.TextField(blank=True, help_text='Notes on how the message was handled or responded to for future reference')
    date = models.DateTimeField(auto_now_add=True, editable=False)
    date_edited = models.DateTimeField(auto_now=True, editable=False)

    @cached_property
    def view_users(self):
        return User.objects.filter(is_superuser=True, is_coordinator=True)
    
    @cached_property
    def handle_users(self):
        return User.objects.filter(is_superuser=True, is_coordinator=True)

    def __str__(self):
        return self.sender


class Quote(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if (user == current_user and current_user.is_quoter) or current_user.is_superuser:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='quotes')
    quote = models.TextField()
    author = models.CharField(max_length=150)
    source = models.CharField(max_length=150, blank=True, null=True)
    fictional = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, editable=False)
    date_edited = models.DateTimeField(auto_now=True, editable=False)

    @cached_property
    def edit_users(self):
        if self.user:
            return User.objects.filter(Q(is_superuser=True) | Q(pk=self.user.pk)).distinct()
        return User.objects.filter(is_superuser=True)

    @cached_property
    def delete_users(self):
        if self.user:
            return User.objects.filter(Q(is_superuser=True) | Q(pk=self.user.pk)).distinct()
        return User.objects.filter(is_superuser=True)
    
    def __str__(self):
        return self.quote + ' - ' + self.author

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('quote'),
                name='unique_quote'
            ),
        ]
        ordering = ['author']


class RecruitmentPost(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or current_user.is_coordinator or (current_user.role == 'recruiter' and current_user.is_approved and current_user == user):
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    job_type_choices = [
        ('FT', 'Full Time'),
        ('PT', 'Part Time'),
        ('IS', 'Internship'),
        ('CT', 'Contract'),
        ('TP', 'Temporary'),
        ('VO', 'Volunteer'),
        ('OT', 'Other'),
    ]
    workplace_type_choices = [
        ('S', 'On site'),
        ('R', 'Remote'),
        ('H', 'Hybrid'),
    ]
    start_date_type_choices = [
        ('I', 'Immediately'),
        ('S', 'Specify'),
    ]
    salary_type_choices = [
        ('S', 'Specified'),
        ('P', 'Performance Based'),
    ]
    user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='recruitment_posts')
    title = models.CharField('Job Title / Designation', max_length=150)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True,
                                help_text='City, Country of the office to be working under.')
    job_type = models.CharField('Type',
                                max_length=2, choices=job_type_choices, default='FT')
    workplace_type = models.CharField('Workplace',
                                      max_length=1, choices=workplace_type_choices, default='S')
    salary_type = models.CharField('Paycheck type',
                                   max_length=1, choices=salary_type_choices, default='S', help_text='Performance based or Specify a range')
    minimum_salary = models.FloatField('Minimum', default=0)
    maximum_salary = models.FloatField('Maximum', default=0)
    fee = models.FloatField(validators=[MinValueValidator(
        0)], default=0, help_text='Any fee to be paid by the applicant.')
    experience_duration = models.SmallIntegerField('Required Experience',
                                                   validators=[MinValueValidator(0)], default=0)
    start_date_type = models.CharField(
        max_length=1, choices=start_date_type_choices, default='I')
    start_date = models.DateField(blank=True, null=True)
    description = models.TextField('Job Description')
    skills = models.ManyToManyField('resume.Skill', related_name='jobs')
    requirements = models.TextField(
        blank=True, help_text='List of requirements for the job other than skills, qualifications, experience etc.')
    required_documents = models.TextField(
        blank=True, help_text='List of documents required from the applicants.')
    questionaires = models.TextField(
        blank=True, help_text='If any information is required from the applicants, list a set of questions or instructions.')
    apply_by = models.DateField(
        default=datetime.now().date() + timedelta(days=7))
    posted_on = models.DateTimeField(auto_now_add=True, editable=False)
    edited_on = models.DateTimeField(auto_now=True, editable=False)
    pending_application_instructions = models.TextField(blank=True)
    rejected_application_instructions = models.TextField(blank=True)
    selected_application_instructions = models.TextField(blank=True)
    shortlisted_application_instructions = models.TextField(blank=True)

    @cached_property
    def edit_users(self):
        if self.user == None:
            User.objects.filter(Q(is_superuser=True) | Q(is_coordinator=True)).distinct()
        if self.user.is_superuser:
            return User.objects.filter(is_superuser=True)
        if self.user.is_coordinator:
            return User.objects.filter(Q(is_superuser=True) | Q(is_coordinator=True)).distinct()
        return User.objects.filter(Q(is_superuser=True) | Q(is_coordinator=True) | Q(pk=self.user.pk)).distinct()

    @cached_property
    def add_skill_users(self):
        if self.user == None:
            User.objects.filter(Q(is_superuser=True) | Q(is_coordinator=True)).distinct()
        return User.objects.filter(Q(is_superuser=True) | Q(is_coordinator=True) | Q(pk=self.user.pk)).distinct()

    @cached_property
    def remove_skill_users(self):
        if self.user == None:
            User.objects.filter(Q(is_superuser=True) | Q(is_coordinator=True)).distinct()
        return User.objects.filter(Q(is_superuser=True) | Q(is_coordinator=True) | Q(pk=self.user.pk)).distinct()

    @cached_property
    def view_application_users(self):
        if self.user == None:
            User.objects.filter(is_superuser=True).distinct()
        return User.objects.filter(Q(is_superuser=True) | Q(pk=self.user.pk)).distinct()

    @cached_property
    def select_application_users(self):
        if self.user == None:
            User.objects.filter(is_superuser=True).distinct()
        return User.objects.filter(Q(is_superuser=True) | Q(pk=self.user.pk)).distinct()

    @cached_property
    def reject_application_users(self):
        if self.user == None:
            User.objects.filter(is_superuser=True).distinct()
        return User.objects.filter(Q(is_superuser=True) | Q(pk=self.user.pk)).distinct()

    @cached_property
    def shortlist_application_users(self):
        if self.user == None:
            User.objects.filter(is_superuser=True).distinct()
        return User.objects.filter(Q(is_superuser=True) | Q(pk=self.user.pk)).distinct()

    @cached_property
    def pending_application_users(self):
        if self.user == None:
            User.objects.filter(is_superuser=True).distinct()
        return User.objects.filter(Q(is_superuser=True) | Q(pk=self.user.pk)).distinct()

    @cached_property
    def is_active(self):
        return self.apply_by >= datetime.now().date()


class RecruitmentPostUpdate(Notice):
    class Manager(Notice.Manager):
        def get_create_permission(self, post, user):
            if user.is_superuser or user.is_coordinator or (user.role == 'recruiter' and user == post.user):
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    recruitment_post = models.ForeignKey(
        RecruitmentPost, on_delete=models.RESTRICT, related_name='updates')
    
    def save(self, *args, **kwargs):
        self.kind = 'U'
        super().save()


class RecruitmentApplication(models.Model):
    class DefaultManager(models.Manager):
        def get_create_permission(self, post, user):
            if (user.role == 'student' and user.is_approved) and post.is_active and not post.applications.filter(user=user).exists():
                return True
            return False

        def get_queryset(self):
            skill_matches = Skill.objects.filter(
                users__id__exact=OuterRef('user_id'),
                jobs__id__exact=OuterRef('recruitment_post_id')
            ).order_by().annotate(
                count=Func('id', function='Count')
            ).values('count')

            skill_extras = Skill.objects.filter(
                users__id__exact=OuterRef('user_id')
            ).exclude(
                jobs__id__exact=OuterRef('recruitment_post_id')
            ).order_by().annotate(
                count=Func('id', function='Count')
            ).values('count')

            queryset = super().get_queryset().annotate(
                skill_matches=Subquery(skill_matches),
                other_skills_count=Subquery(skill_extras)
            )

            return queryset

    objects = DefaultManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recruitment_post'],
                name='unique_application'
            ),
        ]

        base_manager_name = 'objects'

    status_choices = [
        ('P', 'Pending'),
        ('R', 'Rejected'),
        ('S', 'Selected'),
        ('I', 'Shortlisted for Interview'),
    ]
    user = models.ForeignKey(
        User, null=True, on_delete=models.CASCADE, related_name='job_applications')
    recruitment_post = models.ForeignKey(
        RecruitmentPost, on_delete=models.RESTRICT, related_name='applications')
    cover_letter = models.TextField(
        help_text='Write a cover letter for the application explaining why you are the best fit for this opportunity.')
    answers = models.TextField(blank=True)
    applied_on = models.DateTimeField(auto_now_add=True, editable=False)
    status = models.CharField(
        max_length=1, choices=status_choices, default='P')

    @cached_property
    def select_users(self):
        if self.status == 'P':
            return self.recruitment_post.select_application_users
        return User.objects.none()

    @cached_property
    def reject_users(self):
        if self.status == 'P':
            return self.recruitment_post.reject_application_users
        return User.objects.none()

    @cached_property
    def shortlist_users(self):
        if self.status == 'P':
            return self.recruitment_post.shortlist_application_users
        return User.objects.none()

    @cached_property
    def pending_users(self):
        if self.status != 'P':
            return self.recruitment_post.pending_application_users
        return User.objects.none()
