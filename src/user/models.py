from django.db import models
from django.db.models import Q
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from random import randint
from django.urls import reverse
from django.utils import timezone

# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    role_choices = [
        ('staff', 'Staff'),
        ('student', 'Student'),
        ('recruiter', 'Recruiter'),
    ]

    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    groups = models.ManyToManyField(
        'auth.Group', blank=True, related_name='users')
    user_permissions = models.ManyToManyField(
        'auth.Permission', blank=True, related_name='users')
    is_approved = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True, editable=False)
    date_joined = models.DateTimeField(auto_now_add=True, editable=False)
    role = models.CharField(
        max_length=20, choices=role_choices, default='staff')

    objects = BaseUserManager()

    USERNAME_FIELD = 'id'

    primary_email = models.OneToOneField(
        'Email', on_delete=models.RESTRICT, editable=False, related_name='primary_of')
    primary_phone_number = models.OneToOneField(
        'PhoneNumber', on_delete=models.RESTRICT, null=True, blank=True, editable=False, related_name='primary_of')
    primary_address = models.OneToOneField(
        'Address', on_delete=models.RESTRICT, null=True, blank=True, editable=False, related_name='primary_of')
    full_name = models.CharField(
        max_length=300, editable=False, blank=True, default='')
    short_name = models.CharField(
        max_length=150, editable=False, blank=True, default='')
    is_coordinator = models.BooleanField(editable=False, default=False)
    is_developer = models.BooleanField(editable=False, default=False)
    is_doctor = models.BooleanField(editable=False, default=False)
    is_quoter = models.BooleanField(editable=False, default=False)

    @property
    def subtext(self):
        subtext = ''
        if self.role == 'student' and hasattr(self, 'student_profile'):
            if self.student_profile.is_current:
                subtext = self.student_profile.course + ' ' + \
                    self.student_profile.semester_name + ' Semester'
            elif self.student_profile.dropped_out:
                subtext = self.student_profile.course + ' ' + 'Drop Out'
            elif self.student_profile.passed_out:
                subtext = self.student_profile.course + ' ' + 'Alumni'
            subtext = (subtext +
                       (', TPC Website Developer' if self.is_developer else '') +
                       (', TPC Website Administrator' if self.is_superuser and not self.is_developer else '') +
                       (', TPC Coordinator' if self.is_coordinator and not self.is_superuser else ''))[::-1].replace(',', 'dna ', 1)[::-1]
        if self.role == 'staff':
            subtext = (self.staff_profile.designation +
                       (', Coordinator' if self.is_coordinator and not self.staff_profile.is_tpc_head and not self.staff_profile.is_hod else '') +
                       (', TPC Head' if self.staff_profile.is_tpc_head else '') +
                       (', HOD' if self.staff_profile.is_hod else ''))[::-1].replace(',', 'dna ', 1)[::-1]
        if self.role == 'recruiter':
            subtext = self.recruiter_profile.designation + \
                ' at ' + self.recruiter_profile.company_name
        return subtext

    def check_if_doctor(self) -> bool:
        yes = False
        if self.role == 'staff' and hasattr(self, 'staff_profile') and self.staff_profile.qualification == 'PhD':
            yes = True
        educations = ['BDS', 'B.Ch', 'BAMS', 'BHMS', 'MBBS',
                      'MDS', 'MCh', 'MAMS', 'MHMS', 'MS', 'MD', 'PhD']
        if yes == False and self.pk and self.other_educations.filter(education__in=educations).exists():
            yes = True
        return yes

    def get_full_name(self):
        if self.is_doctor:
            return f'Dr. {self.first_name} {self.last_name}'
        else:
            return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        if self.is_doctor:
            return f'Dr. {self.last_name}'
        else:
            return self.first_name

    @property
    def reset_password_users(self):
        return User.objects.filter(pk=self.pk)

    @property
    def set_password_users(self):
        if self.is_superuser:
            return User.objects.filter(pk=self.pk)
        return User.objects.filter(is_superuser=True)

    @property
    def edit_users(self):
        if self.is_superuser:
            return User.objects.filter(pk=self.pk)
        return User.objects.filter(Q(is_superuser=True) | Q(pk=self.pk)).distinct()

    @property
    def view_users(self):
        if self.is_superuser or self.is_coordinator or self.role == 'staff' or self.role == 'recruiter' or (self.role == 'student' and self.student_profile.is_cr):
            return User.objects.all()
        if self.role == 'student':
            return User.objects.filter(
                Q(is_superuser=True) | Q(is_coordinator=True) | Q(pk=self.pk) |
                Q(
                    Q(recruitment_posts__applications__in=self.job_applications.all())
                ) |
                Q(
                    Q(student_profile__registration_year=self.student_profile.registration_year) & Q(
                        student_profile__course=self.student_profile.course) & Q(student_profile__is_cr=True)
                ) |
                Q(
                    Q(student_profile__pass_out_year=self.student_profile.pass_out_year) & Q(
                        student_profile__course=self.student_profile.course) & Q(student_profile__is_cr=True)
                )
            ).distinct()

    @property
    def approve_users(self):
        if self.is_approved or not self.primary_email.is_verified:
            return User.objects.none()
        return User.objects.filter(Q(Q(is_superuser=True) | Q(is_coordinator=True))).distinct()

    @property
    def delete_users(self):
        if self.is_approved:
            return User.objects.none()
        return User.objects.filter(Q(Q(is_superuser=True) | Q(is_coordinator=True))).distinct()

    @property
    def make_superuser_users(self):
        if self.is_superuser or not self.primary_email.is_verified:
            return User.objects.none()
        return User.objects.filter(is_superuser=True)

    @property
    def make_coordinator_users(self):
        if self.is_coordinator or not self.primary_email.is_verified:
            return User.objects.none()
        return User.objects.filter(Q(Q(is_superuser=True) | Q(is_coordinator=True))).distinct()

    @property
    def remove_coordinator_users(self):
        if self.is_superuser or not self.is_coordinator:
            return User.objects.none()
        if self.is_coordinator:
            return User.objects.filter(is_superuser=True)

    @property
    def make_quoter_users(self):
        if self.is_quoter or not self.is_approved:
            return User.objects.none()
        return User.objects.filter(is_superuser=True)

    @property
    def remove_quoter_users(self):
        if not self.is_quoter:
            return User.objects.none()
        return User.objects.filter(is_superuser=True)

    @property
    def make_cr_users(self):
        if not hasattr(self, 'student_profile') or self.student_profile.is_cr or not self.primary_email.is_verified:
            return User.objects.none()
        return User.objects.filter(
            Q(is_superuser=True) | Q(is_coordinator=True) |
            Q(
                Q(student_profile__registration_year=self.student_profile.registration_year) &
                Q(student_profile__course=self.student_profile.course) &
                Q(student_profile__is_cr=True)
            )
        ).distinct()

    @property
    def remove_cr_users(self):
        if not hasattr(self, 'student_profile') or not self.student_profile.is_cr:
            return User.objects.none()
        return User.objects.filter(
            Q(is_superuser=True) | Q(is_coordinator=True) | Q(pk=self.pk)
        )

    @property
    def make_hod_users(self):
        if not hasattr(self, 'staff_profile') or self.staff_profile.is_hod or not self.primary_email.is_verified:
            return User.objects.none()
        return User.objects.filter(Q(is_superuser=True) | Q(staff_profile__is_hod=True)).distinct()

    @property
    def make_tpc_head_users(self):
        if not hasattr(self, 'staff_profile') or self.staff_profile.is_tpc_head or not self.primary_email.is_verified:
            return User.objects.none()
        return User.objects.filter(Q(is_superuser=True) | Q(staff_profile__is_hod=True) | Q(staff_profile__is_tpc_head=True)).distinct()

    def save(self, *args, **kwargs):
        self.is_doctor = self.check_if_doctor()
        self.full_name = self.get_full_name()
        self.short_name = self.get_short_name()
        if self.is_superuser or self.is_coordinator:
            self.is_approved = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.id}' + '(' + self.full_name + ')'


class PhoneNumber(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    country_code = models.PositiveSmallIntegerField(default=91)
    phone_number = models.PositiveBigIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             null=True, blank=True, related_name='phone_numbers')

    @property
    def set_primary_users(self):
        if self == self.user.primary_phone_number:
            return User.objects.none()
        if self.user.is_superuser:
            return User.objects.filter(pk=self.user.pk)
        return User.objects.filter(Q(Q(is_superuser=True) | Q(pk=self.user.pk))).distinct()

    @property
    def delete_users(self):
        if self == self.user.primary_phone_number:
            return User.objects.none()
        if self.user.is_superuser:
            return User.objects.filter(pk=self.user.pk)
        return User.objects.filter(Q(Q(is_superuser=True) | Q(pk=self.user.pk))).distinct()

    def save(self, *args, **kwargs):
        if not PhoneNumber.objects.filter(user=self.user).exists() and self.user != None:
            self.user.primary_phone_number = self
        if hasattr(self, 'primary_of') and self.primary_of:
            self.user = self.primary_of
        super().save(*args, **kwargs)
        if self.user:
            self.user.save()

    def __str__(self):
        return '+' + str(self.country_code) + '-' + str(self.phone_number)


class Email(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    email = models.EmailField(unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='emails')
    is_verified = models.BooleanField(default=False)
    verify_code = models.CharField(max_length=12, editable=False, blank=True, null=True)
    verify_code_time = models.DateTimeField(editable=False, blank=True, null=True)
    verify_code_valid_for = models.SmallIntegerField(default=5, editable=False)
    
    @property
    def verify_code_valid(self):
        if self.verify_code and self.verify_code_time:
            return (timezone.now() - self.verify_code_time).seconds < (self.verify_code_valid_for * 60)
        return False

    @property
    def set_primary_users(self):
        if self == self.user.primary_email or not self.is_verified:
            return User.objects.none()
        if self.user.is_superuser:
            return User.objects.filter(pk=self.user.pk)
        return User.objects.filter(Q(Q(is_superuser=True) | Q(pk=self.user.pk))).distinct()

    @property
    def delete_users(self):
        if self == self.user.primary_email:
            return User.objects.none()
        if self.user.is_superuser:
            return User.objects.filter(pk=self.user.pk)
        return User.objects.filter(Q(Q(is_superuser=True) | Q(pk=self.user.pk))).distinct()

    @property
    def verify_users(self):
        if self.is_verified:
            return User.objects.none()
        return User.objects.filter(Q(is_superuser=True) | Q(pk=self.user.pk)).distinct()

    def send_verification_email(self, request):
        self.verify_code = str(randint(100000000000, 999999999999))
        self.save()
        subject = 'Email Verification | TPC | CSE | AUS'
        url = request.build_absolute_uri(reverse('verify_email', args=[self.pk, self.verify_code]))
        html_message = render_to_string(
            'email_verification.html',
            {
                'verification_url': url,
                'valid_for': self.verify_code_valid_for,
            }
        )
        print(f'Email: {self.email} Verification link: {url}')
        try:
            return send_mail(subject=subject, message=strip_tags(html_message), from_email=None, recipient_list=[self.email], html_message=html_message)
        except:
            return 0

    def save(self, *args, **kwargs):
        if not Email.objects.filter(user=self.user).exists() and self.user:
            self.user.primary_email = self
        if hasattr(self, 'primary_of') and self.primary_of:
            self.user = self.primary_of
        if self.verify_code:
            self.verify_code_time = timezone.now()
        else:
            self.verify_code_time = None

        super().save(*args, **kwargs)
        if self.user:
            self.user.save()

    def __str__(self):
        return self.email


class Address(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='addresses')
    address = models.TextField()
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    country = models.CharField(max_length=150)
    pincode = models.PositiveIntegerField('PIN/ZIP Code')

    @property
    def edit_users(self):
        if self.user.is_superuser:
            return User.objects.filter(pk=self.user.pk)
        return User.objects.filter(Q(Q(is_superuser=True) | Q(pk=self.user.pk))).distinct()

    @property
    def set_primary_users(self):
        if self == self.user.primary_address:
            return User.objects.none()
        if self.user.is_superuser:
            return User.objects.filter(pk=self.user.pk)
        return User.objects.filter(Q(Q(is_superuser=True) | Q(pk=self.user.pk))).distinct()

    @property
    def delete_users(self):
        if self == self.user.primary_address:
            return User.objects.none()
        if self.user.is_superuser:
            return User.objects.filter(pk=self.user.pk)
        return User.objects.filter(Q(Q(is_superuser=True) | Q(pk=self.user.pk))).distinct()

    def save(self, *args, **kwargs):
        if not Address.objects.filter(user=self.user).exists() and self.user != None:
            self.user.primary_address = self
        if hasattr(self, 'primary_of') and self.primary_of:
            self.user = self.primary_of
        super().save(*args, **kwargs)
        if self.user:
            self.user.save()

    def __str__(self):
        return self.address + ', ' + self.city + ', ' + self.state + ', ' + self.country + ' - ' + str(self.pincode)


class Link(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='links')
    url = models.URLField()
    title = models.CharField(max_length=150)

    icons = {
        'linkedin': 'bi bi-linkedin',
        'github': 'bi bi-github',
        'twitter': 'bi bi-twitter',
        'facebook': 'bi bi-facebook',
        'instagram': 'bi bi-instagram',
        'youtube': 'bi bi-youtube',
        'medium': 'bi bi-medium',
        'twitch': 'bi bi-twitch',
        'discord': 'bi bi-discord',
        'whatsapp': 'bi bi-whatsapp',
        'telegram': 'bi bi-telegram',
        'snapchat': 'bi bi-snapchat',
        'reddit': 'bi bi-reddit',
        'tiktok': 'bi bi-tiktok',
        'pinterest': 'bi bi-pinterest',
        'behance': 'bi bi-behance',
        'dribbble': 'bi bi-dribbble',
        'paypal': 'bi bi-paypal',
        'google': 'bi bi-google',
        'apple': 'bi bi-apple',
        'microsoft': 'bi bi-microsoft',
        'amazon': 'bi bi-amazon',
        'spotify': 'bi bi-spotify',
    }

    @property
    def icon(self):
        for key, value in self.icons.items():
            if key in self.url.split('.')[0]:
                return value
        return 'bi bi-link-45deg'

    @property
    def set_primary_users(self):
        if self.user.is_superuser:
            return User.objects.filter(pk=self.user.pk)
        return User.objects.filter(Q(Q(is_superuser=True) | Q(pk=self.user.pk))).distinct()

    @property
    def delete_users(self):
        if self.user.is_superuser:
            return User.objects.filter(pk=self.user.pk)
        return User.objects.filter(Q(Q(is_superuser=True) | Q(pk=self.user.pk))).distinct()

    def __str__(self):
        return self.title + ' : ' + self.url
