from django.db import models
from django.db.models import Q
from user.models import User

# Create your models here.


class StaffProfile(models.Model):
    qualification_choices = [
        ('PhD', 'Doctor of Philosophy'),
        ('M.Phil', 'Master of Philosophy'),
        ('M.Tech', 'Master of Technology'),
        ('MCA', 'Master of Computer Applications'),
        ('ME', 'Master of Engineering'),
        ('MBA', 'Master of Business Administration'),
        ('M.Arch', 'Master of Architecture'),
        ('MSc', 'Master of Science'),
        ('LLM', 'Master of Law'),
        ('M.Ed', 'Master of Education'),
        ('M.Des', 'Master of Design'),
        ('M.Com', 'Master of Commerce'),
        ('MA', 'Master of Arts'),
        ('B.Tech', 'Bachelor of Technology'),
        ('BCA', 'Bachelor of Computer Applications'),
        ('BE', 'Bachelor of Engineering'),
        ('BBA', 'Bachelor of Business Administration'),
        ('B.Arch', 'Bachelor of Architecture'),
        ('BSc', 'Bachelor of Science'),
        ('LLB', 'Bachelor of Law'),
        ('B.Ed', 'Bachelor of Education'),
        ('B.Des', 'Bachelor of Design'),
        ('B.Com', 'Bachelor of Commerce'),
        ('BA', 'Bachelor of Arts'),
        ('Others', 'Others'),
    ]
    designation_choices = [
        ('Professor', 'Professor'),
        ('Assistant Professor', 'Assistant Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Lecturer', 'Lecturer'),
        ('Guest Faculty', 'Guest Faculty'),
        ('Teaching Assistant', 'Teaching Assistant'),
        ('Instructor', 'Instructor'),
        ('Lab Attendant', 'Lab Attendant'),
        ('Research Assistant', 'Research Assistant'),
        ('Technical Staff', 'Technical Staff'),
        ('Non-Teaching Staff', 'Non-Teaching Staff'),
        ('Others', 'Others'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='staff_profile')
    id_number = models.CharField('ID Number', max_length=50, blank=True, null=True, unique=True)
    qualification = models.CharField(
        max_length=6, choices=qualification_choices, default='others')
    designation = models.CharField(
        max_length=20, choices=designation_choices, default='others')
    is_hod = models.BooleanField(default=False)
    is_tpc_head = models.BooleanField(default=False)

    @property
    def edit_users(self):
        if self.user.is_superuser:
            return User.objects.filter(pk=self.user.pk)
        return User.objects.filter(Q(Q(is_superuser=True) | Q(pk=self.user.pk))).distinct()

    @property
    def view_users(self):
        return User.objects.all()

    @property
    def make_hod_users(self):
        return User.objects.filter(Q(is_superuser=True) | Q(staff_profile__is_hod=True)).distinct()

    @property
    def make_tpc_head_users(self):
        return User.objects.filter(Q(is_superuser=True) | Q(staff_profile__is_hod=True) | Q(staff_profile__is_tpc_head=True)).distinct()

    def save(self, *args, **kwargs):
        if self.is_hod:
            StaffProfile.objects.filter(is_hod=True).update(is_hod=False)
            self.user.is_coordinator = True
        if self.is_tpc_head:
            StaffProfile.objects.filter(
                is_tpc_head=True).update(is_tpc_head=False)
            self.user.is_coordinator = True
        super().save(*args, **kwargs)
        self.user.save()

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name
