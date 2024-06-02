from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
import datetime

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, id, password=None):
        if not id:
            raise ValueError("Users must have an id")

        user = self.model(
            id=id
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, id, password=None):
        user = self.create_user(
            id=id,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    role_choices = [
        ('staff', 'Staff'),
        ('student', 'Student'),
        ('recruiter', 'Recruiter'),
    ]

    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
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
    role = models.CharField(max_length=20, choices=role_choices, default='staff')

    objects = UserManager()

    USERNAME_FIELD = 'id'

    primary_email = models.EmailField(editable=False, null=True, blank=True)
    primary_phone_number = models.PositiveBigIntegerField(editable=False, null=True, blank=True)
    full_name = models.CharField(max_length=300, editable=False, blank=True, default='')
    short_name = models.CharField(max_length=150, editable=False, blank=True, default='')
    is_coordinator = models.BooleanField(editable=False, default=False)
    is_doctor = models.BooleanField(editable=False, default=False)
    
    @property
    def age(self):
        return int((datetime.date.today() - self.date_of_birth).days / 365.25) if self.date_of_birth else None

    @property
    def primary_address(self):
        return self.addresses.get(user=self, is_primary=True) if self.addresses.filter(user=self, is_primary=True).exists() else None

    @property
    def subtext(self):
        subtext = ''
        if self.role == 'student' and hasattr(self, 'student_profile'):
            subtext = self.student_profile.course + ' ' + \
                self.student_profile.semester_name + ' Semester'
        if self.role == 'staff':
            subtext = self.staff_profile.designation + ' and ' + \
                ('HOD' if self.staff_profile.is_hod else 'TPC Head' if self.staff_profile.is_tpc_head else '')
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
        if self.check_if_doctor():
            return f'Dr. {self.first_name} {self.last_name}'
        else:
            return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        if self.check_if_doctor():
            return f'Dr. {self.last_name}'
        else:
            return self.first_name

    def save(self, *args, **kwargs):
        if self.pk:
            if self.emails.filter(user=self, is_primary=True).exists():
                self.primary_email = self.emails.get(user=self, is_primary=True).email
            else:
                self.primary_email = None
            if self.phone_numbers.filter(user=self, is_primary=True).exists():
                self.primary_phone_number = self.phone_numbers.get(user=self, is_primary=True).phone_number
            else:
                self.primary_phone_number = None
        self.full_name = self.get_full_name()
        self.short_name = self.get_short_name()
        if self.pk:
            self.is_coordinator = self.groups.filter(name='coordinators').exists()
        self.is_doctor = self.check_if_doctor()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.id}' + '(' + self.full_name + ')'


class PhoneNumber(models.Model):
    country_code = models.PositiveSmallIntegerField(default=91)
    phone_number = models.PositiveBigIntegerField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='phone_numbers')
    is_primary = models.BooleanField('Set as Primary', default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            PhoneNumber.objects.filter(user=self.user).update(is_primary=False)
        elif not PhoneNumber.objects.filter(user=self.user, is_primary=True).exists():
                self.is_primary = True
        super().save(*args, **kwargs)

    def __str__(self):
        return '+' + str(self.country_code) + '-' + str(self.phone_number)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['country_code', 'phone_number'], name='unique_phone_number'),
            models.UniqueConstraint(fields=['user'], condition=models.Q(is_primary=True), name='unique_primary_phone_number'),
        ]


class Email(models.Model):
    email = models.EmailField(unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='emails')
    is_primary = models.BooleanField('Set as Primary', default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            Email.objects.filter(user=self.user).update(is_primary=False)
        elif not Email.objects.filter(user=self.user, is_primary=True).exists():
            self.is_primary = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], condition=models.Q(is_primary=True), name='unique_primary_email')
        ]


class Address(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='addresses')
    address = models.TextField()
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    country = models.CharField(max_length=150)
    pincode = models.PositiveIntegerField('PIN/ZIP Code')
    is_primary = models.BooleanField('Set as Primary', default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            Address.objects.filter(user=self.user).update(is_primary=False)
        elif not Address.objects.filter(user=self.user, is_primary=True).exists():
            self.is_primary = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.address + ', ' + self.city + ', ' + self.state + ', ' + self.country + ' - ' + str(self.pincode)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], condition=models.Q(is_primary=True), name='unique_primary_address')
        ]


class Link(models.Model):
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

    def __str__(self):
        return self.title + ' : ' + self.url