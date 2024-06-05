from django.db import models
from django.db.models.functions import Lower
from django.core.validators import MaxValueValidator, MinValueValidator
from user.models import User

# Create your models here.


class Notice(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True, editable=False)
    date_edited = models.DateTimeField(auto_now=True, editable=False)
    added_by = models.ForeignKey(
        'user.User', null=True, on_delete=models.SET_NULL, related_name='notices')

    def __str__(self):
        return self.title


class Message(models.Model):
    sender = models.CharField(max_length=150)
    sender_designation = models.CharField(max_length=150)
    sender_company = models.CharField(max_length=150)
    sender_phone = models.CharField(max_length=150)
    sender_email = models.EmailField()
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True, editable=False)
    date_edited = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.sender


class Quote(models.Model):
    quote = models.TextField()
    author = models.CharField(max_length=150)
    source = models.CharField(max_length=150, blank=True, null=True)
    fictional = models.BooleanField(default=False)

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
    currency_choices = [
        ('INR', '(INR) ₹'),
        ('USD', '(USD) $'),
        ('EUR', '(EUR) €'),
        ('GBP', '(GBP) £'),
        ('JPY', '(JPY) ¥'),
        ('CNY', '(CNY) ¥'),
        ('AUD', '(AUD) $'),
        ('CAD', '(CAD) $'),
        ('CHF', '(CHF) Fr'),
        ('SEK', '(SEK) kr'),
        ('NZD', '(NZD) $'),
        ('KRW', '(KRW) ₩'),
        ('SGD', '(SGD) $'),
        ('NOK', '(NOK) kr'),
        ('MXN', '(MXN) $'),
        ('HKD', '(HKD) $'),
        ('TRY', '(TRY) ₺'),
        ('RUB', '(RUB) ₽'),
        ('INR', '(INR) ₹'),
        ('BRL', '(BRL) R$'),
        ('ZAR', '(ZAR) R'),
        ('TWD', '(TWD) NT$'),
        ('DKK', '(DKK) kr'),
        ('PLN', '(PLN) zł'),
        ('THB', '(THB) ฿'),
        ('IDR', '(IDR) Rp'),
        ('HUF', '(HUF) Ft'),
        ('CZK', '(CZK) Kč'),
        ('ILS', '(ILS) ₪'),
        ('CLP', '(CLP) $'),
        ('PHP', '(PHP) ₱'),
        ('AED', '(AED) د.إ'),
        ('COP', '(COP) $'),
        ('SAR', '(SAR) ر.س'),
        ('MYR', '(MYR) RM'),
        ('VND', '(VND) ₫'),
        ('IQD', '(IQD) ع.د'),
        ('KWD', '(KWD) د.ك'),
        ('NGN', '(NGN) ₦'),
        ('EGP', '(EGP) E£'),
        ('PKR', '(PKR) Rs'),
        ('BDT', '(BDT) ৳'),
        ('QAR', '(QAR) ر.ق'),
        ('OMR', '(OMR) ر.ع.'),
        ('LKR', '(LKR) Rs'),
    ]
    user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='recruitment_posts')
    title = models.CharField('Job Title / Designation', max_length=150)
    company = models.CharField(max_length=100)
    job_type = models.CharField('Type',
                                max_length=2, choices=job_type_choices, default='FT')
    workplace_type = models.CharField('Workplace',
                                      max_length=1, choices=workplace_type_choices, default='S')
    sallary_currency = models.CharField(
        max_length=3, choices=currency_choices, default='INR')
    sallary = models.CharField(max_length=50, default='Negotiable', help_text='Example: 40 KPM, 4-6 LPA etc.')
    fee_currency = models.CharField(
        max_length=3, choices=currency_choices, default='INR')
    fee = models.FloatField(validators=[MinValueValidator(0)], default=0, help_text='Any fee to be paid by the applicant.')
    description = models.TextField('Job Description')
    is_active = models.BooleanField(default=True, help_text='Uncheck to stop receiving applications.')
    posted_on = models.DateTimeField(auto_now_add=True, editable=False)
    pending_application_instructions = models.TextField(blank=True)
    rejected_application_instructions = models.TextField(blank=True)
    selected_application_instructions = models.TextField(blank=True)
    shortlisted_application_instructions = models.TextField(blank=True)


class RecruitmentPostUpdate(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    recruitment_post = models.ForeignKey(
        RecruitmentPost, on_delete=models.RESTRICT, related_name='updates')
    user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='recruitment_post_updates')
    shared_on = models.DateTimeField(auto_now_add=True, editable=False)


class RecruitmentApplication(models.Model):
    status_choices = [
        ('P', 'Pending'),
        ('R', 'Rejected'),
        ('S', 'Selected'),
        ('I', 'Shortlisted for Interview'),
    ]
    user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='job_applications')
    recruitment_post = models.ForeignKey(
        RecruitmentPost, on_delete=models.RESTRICT, related_name='applications')
    cover_letter = models.TextField()
    applied_on = models.DateTimeField(auto_now_add=True, editable=False)
    status = models.CharField(
        max_length=1, choices=status_choices, default='P')
