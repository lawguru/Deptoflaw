from django.db import models
from django.db.models.functions import Lower
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Q
from user.models import User

# Create your models here.


class OtherEducation(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    education_choices = [
        ('Schooling', (
            ('HSLC', 'High School Leaving Certificate'),
            ('HS', 'Higher Secondary Education or 10+2 equivalent'),
        ),
        ),
        ('Diploma', (
            ('D.Music', 'Diploma in Music'),
            ('D.Dance', 'Diploma in Dance'),
            ('Drama', 'Diploma in Drama'),
            ('D.Litt', 'Diploma in Literature'),
            ('D.El.Ed', 'Diploma in Elementary Education'),
            ('D.P.Ed', 'Diploma in Physical Education'),
            ('D.Sc', 'Diploma in Science'),
            ('DCA', 'Diploma in Computer Applications'),
            ('DTP', 'Diploma in Desktop Publishing'),
            ('DHS', 'Diploma in Health Science'),
            ('DMS', 'Diploma in Medical Science'),
            ('DMB', 'Diploma in Medical Biotechnology'),
            ('DMSW', 'Diploma in Medical and Social Work'),
            ('DPT', 'Diploma in Physiotherapy'),
            ('DML', 'Diploma in Medical Laboratory'),
            ('DMLT', 'Diploma in Medical Laboratory Technology'),
            ('DMLIS', 'Diploma in Medical Library and Information Science'),
            ('GNM', 'General Nursing and Midwifery'),
            ('ANM', 'Auxiliary Nursing and Midwifery'),
            ('DAMS', 'Diploma in Ayurvedic Medicine and Surgery'),
            ('DHMS', 'Diploma in Homeopathic Medicine and Surgery'),
            ('DMLT', 'Diploma in Medical Laboratory Technology'),
            ('D.Phil', 'Diploma in Philosophy'),
        ),
        ),
        ('Bachelor', (
            ('BA', 'Bachelor of Arts'),
            ('BFA', 'Bachelor of Fine Arts'),
            ('BPA', 'Bachelor of Performing Arts'),
            ('BVA', 'Bachelor of Visual Arts'),
            ('B.Com', 'Bachelor of Commerce'),
            ('B.Ed', 'Bachelor of Education'),
            ('B.P.Ed', 'Bachelor of Physical Education'),
            ('BSc', 'Bachelor of Science'),
            ('BCA', 'Bachelor of Computer Applications'),
            ('BBA', 'Bachelor of Business Administration'),
            ('B.Arch', 'Bachelor of Architecture'),
            ('B.Tech', 'Bachelor of Technology'),
            ('B.Pharm', 'Bachelor of Pharmacy'),
            ('B.PH', 'Bachelor of Public Health'),
            ('BPT', 'Bachelor of Physiotherapy'),
            ('BDS', 'Bachelor of Dental Surgery'),
            ('B.Ch', 'Bachelor of Chirurgiae'),
            ('BAMS', 'Bachelor of Ayurvedic Medicine and Surgery'),
            ('BHMS', 'Bachelor of Homeopathic Medicine and Surgery'),
            ('MBBS', 'Bachelor of Medicine, Bachelor of Surgery'),
            ('LLB', 'Bachelor of Laws'),
            ('BBA LLB', 'Bachelor of Business Administration, Bachelor of Laws'),
            ('B.Phil', 'Bachelor of Philosophy'),
        ),
        ),
        ('Master', (
            ('MA', 'Master of Arts'),
            ('MFA', 'Master of Fine Arts'),
            ('MPA', 'Master of Performing Arts'),
            ('MVA', 'Master of Visual Arts'),
            ('M.Com', 'Master of Commerce'),
            ('M.Ed', 'Master of Education'),
            ('M.P.Ed', 'Master of Physical Education'),
            ('MSc', 'Master of Science'),
            ('MCA', 'Master of Computer Applications'),
            ('MBA', 'Master of Business Administration'),
            ('M.Arch', 'Master of Architecture'),
            ('M.Tech', 'Master of Technology'),
            ('M.Pharm', 'Master of Pharmacy'),
            ('M.PH', 'Master of Public Health'),
            ('MPT', 'Master of Physiotherapy'),
            ('MDS', 'Master of Dental Surgery'),
            ('M.Ch', 'Master of Chirurgiae'),
            ('MAMS', 'Master of Ayurvedic Medicine and Surgery'),
            ('MHMS', 'Master of Homeopathic Medicine and Surgery'),
            ('MS', 'Master of Surgery'),
            ('LLM', 'Master of Laws'),
            ('MBA LLB', 'Master of Business Administration, Bachelor of Laws'),
            ('M.Phil', 'Master of Philosophy'),
        ),
        ),
        ('Doctorate', (
            ('MD', 'Doctor of Medicine'),
            ('PhD', 'Doctor of Philosophy'),
        ),
        ),
        ('Others', 'Others'),
    ]
    user = models.ForeignKey(
        'user.User', on_delete=models.CASCADE, related_name='other_educations')
    education = models.CharField(
        max_length=10, choices=education_choices, default='HSLC', null=False, blank=False)
    specialization = models.CharField(
        max_length=150, help_text='BOARD, Major, Branch, Research Area etc. Put full form of Abbreviation in brackets. Eg. CBSE (Central Board of Secondary Education)')
    institution = models.CharField(
        max_length=150, help_text='University, College or School Name. You can put full form of Abbreviation in brackets. Eg. KV (Kendriya Vidyalaya)')
    grade_point = models.FloatField('Grades or Percentage', validators=[MinValueValidator(
        0), MaxValueValidator(10)], default=0, help_text='out of 10 or divide by 10 if out of 100')
    year = models.PositiveSmallIntegerField('Passout Year', help_text='Passout year', default=2000, validators=[
                                            MinValueValidator(1900), MaxValueValidator(2100)])
    duration = models.PositiveSmallIntegerField(
        help_text='Duration in years', default=3, validators=[MinValueValidator(1), MaxValueValidator(20)])

    @property
    def edit_users(self):
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
        self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.education + ' from ' + self.institution + ' in ' + str(self.year)
    
    class Meta:
        ordering = ['-year']


class Certification(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='certifications')
    title = models.CharField(max_length=100)
    issuer = models.CharField(max_length=100)
    issue_date = models.DateField()
    description = models.TextField()

    @property
    def edit_users(self):
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

    def __str__(self):
        return f'{self.title} from {self.issuer}'

    class Meta:
        ordering = ['-issue_date']
        constraints = [
            models.UniqueConstraint(fields=['user', 'title'], name='unique_certification'),
        ]


class Skill(models.Model):
    class Manager(models.Manager):
        def get_add_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False
        
        def get_remove_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    users = models.ManyToManyField('user.User', related_name='skills')
    name = models.CharField('I am skilled in', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(Lower('name'), name='unique_skill'),
        ]


class Language(models.Model):
    class Manager(models.Manager):
        def get_add_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

        def get_remove_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    users = models.ManyToManyField('user.User', related_name='languages')
    name = models.CharField('I can speak', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(Lower('name'), name='unique_language'),
        ]


class WorkExperience(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='work_experiences')
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()

    @property
    def edit_users(self):
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

    def __str__(self):
        return f'{self.title} at {self.company}'

    class Meta:
        verbose_name = 'Work Experience'
        verbose_name_plural = 'Work Experiences'
        ordering = ['-start_date']


class Project(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=100)
    description = models.TextField()
    urls = models.TextField('Related URLs', default='', blank=True, help_text='Comma \',\' separated list of URLs in brackets following names. Eg. GitHub Repository (https://github.com/user/repo/), Website (https://example.com/), etc.')
    start_date = models.DateField()
    end_date = models.DateField()

    @property
    def edit_users(self):
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

    def get_name_url_tuple(self):
        urls = self.urls.split(',')
        name_url_tuple = []
        for url in urls:
            if '(' not in url or ')' not in url:
                continue
            name, url = url.split('(')
            name = name.strip()
            url = url.split(')')[0].strip()
            name_url_tuple.append((name, url))
        return name_url_tuple

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-start_date']


class Patent(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='patents')
    title = models.CharField(max_length=100)
    patent_office = models.CharField(max_length=100)
    patent_number = models.CharField(max_length=100)
    issue_date = models.DateField()
    description = models.TextField()

    @property
    def edit_users(self):
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

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-issue_date']


class Publication(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='publications')
    title = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    publication_date = models.DateField()
    description = models.TextField()

    @property
    def edit_users(self):
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

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-publication_date']


class Achievement(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField()

    @property
    def edit_users(self):
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

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date']


class Presentation(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='presentations')
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField()

    @property
    def edit_users(self):
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

    def __str__(self):
        return self.title


class OtherInfo(models.Model):
    class Manager(models.Manager):
        def get_create_permission(self, user, current_user):
            if current_user.is_superuser or user == current_user:
                return True
            return False

    objects = Manager()

    class Meta:
        base_manager_name = 'objects'

    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='other_infos')
    title = models.CharField(max_length=100)
    description = models.TextField()

    @property
    def edit_users(self):
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

    def __str__(self):
        return self.title