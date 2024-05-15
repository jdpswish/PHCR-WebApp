from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date

class User(AbstractUser):
    username = models.CharField(unique=True, max_length=200)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, default='')
    last_name = models.CharField(max_length=255, default='')
    birth_date = models.DateField()
    email_address = models.EmailField(max_length=254, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    position = models.CharField(max_length=50, blank=True)


    REQUIRED_FIELDS = []

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.IntegerField(blank=True, null=True)
    sex = models.CharField(max_length=6, choices=[('Male', 'Male'), ('Female', 'Female')])

    CIVIL_STATUS_CHOICES = [
        ('Married', 'Married'),
        ('Single', 'Single'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
    ]

    civil_status = models.CharField(max_length=50, choices=CIVIL_STATUS_CHOICES, blank=True, default='')
    religion = models.CharField(max_length=50, blank=True, default='')
    address = models.CharField(max_length=100, blank=True, default='')
    educational_attainment = models.CharField(max_length=100, blank=True, default='')
    occupation = models.CharField(max_length=100, blank=True, default='')

    def save(self, *args, **kwargs):
        if not self.age:
            today = date.today()
            birth_date = self.user.birth_date  
            delta_in_years = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            self.age = delta_in_years
        super().save(*args, **kwargs)

CustomUser = get_user_model()

class PasswordChangeRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    new_password = models.CharField(max_length=128)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

class EconomicNumbers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    philhealth_num = models.CharField(max_length=15, blank=True)
    nhts_num = models.CharField(max_length=50, blank=True)
    patient_4ps_member = models.BooleanField(default=False)
    brgy_num = models.CharField(max_length=30, blank=True)
    family_num = models.CharField(max_length=50, blank=True)

class SocialHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alcohol_intake = models.BooleanField(default=False)
    prohibited_drug = models.BooleanField(default=False)
    smoker = models.BooleanField(default=False)
    cigarette_sticks_per_day = models.IntegerField(blank=True, null=True, default=0)

class MedicalHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    diabetes = models.BooleanField(default=False)
    asthma = models.BooleanField(default=False)
    hypertension = models.BooleanField(default=False)
    pulmonary_tubercolosis = models.BooleanField(default=False)
    cancer = models.BooleanField(default=False)
    cough_2_weeks = models.BooleanField(default=False)
    other_medical_history = models.CharField(max_length=255, blank=True)
    medication_taken = models.CharField(max_length=255, blank=True)
    family_planning = models.BooleanField(default=False)
    immunization = models.CharField(max_length=100, blank=True)
    immunization_date = models.DateField(blank=True, null=True, default="")

class DoctorOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chief_complaint = models.TextField(blank=True)
    findings = models.TextField(blank=True)
    impression = models.TextField(blank=True)
    management = models.TextField(blank=True)
    filled_datetime = models.DateTimeField(default=timezone.now)
    filled_by = models.ForeignKey(User, related_name='filled_doctor_order', on_delete=models.SET_NULL, null=True)

class NurseNotes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    admission_date = models.DateField(blank=True, null=True, default=timezone.now)
    admission_time = models.CharField(max_length=50, blank=True)
    subjective_complaint = models.CharField(max_length=100, blank=True)
    objective_findings = models.CharField(max_length=100, blank=True)
    implementation = models.CharField(max_length=100, blank=True)
    assessment = models.CharField(max_length=100, blank=True)
    plan = models.CharField(max_length=100, blank=True)
    filled_datetime = models.DateTimeField(default=timezone.now)
    filled_by = models.ForeignKey(User, related_name='filled_nurse_notes', on_delete=models.SET_NULL, null=True)

class VitalSigns(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight_in_kg = models.FloatField(blank=True, null=True)
    height_in_cm = models.FloatField(blank=True, null=True)
    nutritional_status = models.CharField(max_length=100, blank=True, null=True)
    BMI = models.FloatField(blank=True, null=True)
    body_temperature = models.FloatField(blank=True, null=True)
    pulse_rate = models.FloatField(blank=True, null=True)
    blood_oxygen_levels = models.FloatField(blank=True, null=True)
    respiratory_rate = models.FloatField(blank=True, null=True)
    blood_pressure = models.CharField(max_length=100, blank=True, null=True)
    filled_by = models.ForeignKey(User, related_name='filled_vital_signs', on_delete=models.SET_NULL, null=True)

class Form(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    datetime_created = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10)
    record_type = models.CharField(max_length=50)

class PediatricDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mother_name = models.CharField(max_length=50, blank=True)
    father_name = models.CharField(max_length=50, blank=True)
    mother_age = models.IntegerField(blank=True, null=True)
    father_age = models.IntegerField(blank=True, null=True)
    birth_order = models.IntegerField(blank=True, null=True)

class ImmunizationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tetanus_toxoid_mother_status = models.CharField(max_length=50, blank=True, default="")
    bcg = models.BooleanField(default=False)
    hepa = models.BooleanField(default=False)
    pental_1 = models.BooleanField(default=False)
    pental_2 = models.BooleanField(default=False)
    pental_3 = models.BooleanField(default=False)
    opv_1 = models.BooleanField(default=False)
    opv_2 = models.BooleanField(default=False)
    opv_3 = models.BooleanField(default=False)
    rota_1 = models.BooleanField(default=False)
    rota_2 = models.BooleanField(default=False)
    rota_3 = models.BooleanField(default=False)
    amv = models.BooleanField(default=False)
    mr = models.BooleanField(default=False)
    mmr = models.BooleanField(default=False)
    other_immunization = models.CharField(max_length=50, blank=True, default="")
    vitamin_a = models.BooleanField(default=False)
    breastfeeding = models.BooleanField(default=False)
    deworming = models.BooleanField(default=False)
    deworm_date = models.DateField(blank=True, default=None, null=True)

class ChildDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place_of_birth = models.CharField(max_length=50, blank=True)
    birth_weight = models.FloatField(blank=True)
    birth_order = models.IntegerField(blank=True, null=True)
    mother_name = models.CharField(max_length=255, blank=True)
    birth_length_in_inches = models.FloatField(blank=True, null=True)
    birth_time = models.CharField(max_length=10, blank=True)

    DELIVERY_TYPE_CHOICES = [
        ('NSD', 'Normal Spontaneous Delivery'),
        ('CS', 'Caesarean Section'),
        ('DOS', 'Delivery Operative Suction'),
    ]
    BREASTFEEDING_CHOICES = [
        ('BF', 'Exclusively Breastfed'),
        ('MIXED', 'Exclusively Mixed Feeding'),
        ('MILK', 'Exclusively Formula Milk'),
    ]

    delivery_type = models.CharField(max_length=10, choices=DELIVERY_TYPE_CHOICES, blank=True, default='')
    breastfeeding_type = models.CharField(max_length=10, choices=BREASTFEEDING_CHOICES, blank=True, default='')
    
class NewbornStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ns_place = models.CharField(max_length=50, blank=True, default='')
    ns_date = models.DateField(blank=True, null=True, default=None)
    bcg_date = models.DateField(blank=True, null=True, default=None)
    bcg_place = models.CharField(max_length=50, blank=True, default='')
    dpt_opv_date = models.DateField(blank=True, null=True, default=None)
    dpt_opv_place = models.CharField(max_length=60, blank=True, default='')
    pcv_date = models.DateField(blank=True, null=True, default=None)
    pcv_place = models.CharField(max_length=50, blank=True, default='')
    ipv_date = models.DateField(blank=True, null=True, default=None)
    ipv_place = models.CharField(max_length=50, blank=True, default='')
    hepa_date = models.DateField(blank=True, null=True, default=None)
    hepa_place = models.CharField(max_length=50, blank=True, default='')

class Announcement(models.Model):
    date = models.DateField()
    photo = models.ImageField(upload_to='announcement_photos/')

class Adult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    economic_numbers = models.ForeignKey('EconomicNumbers', on_delete=models.CASCADE)
    social_history = models.ForeignKey('SocialHistory', on_delete=models.CASCADE)
    medical_history = models.ForeignKey('MedicalHistory', on_delete=models.CASCADE)
    doctor_order = models.ForeignKey(DoctorOrder, on_delete=models.CASCADE, null=True)
    nurse_notes = models.ForeignKey(NurseNotes, on_delete=models.CASCADE, null=True)
    vital_signs = models.ForeignKey(VitalSigns, on_delete=models.CASCADE, null=True)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)

class Pediatric(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    economic_numbers = models.ForeignKey(EconomicNumbers, on_delete=models.CASCADE)
    social_history = models.ForeignKey(SocialHistory, on_delete=models.CASCADE)
    medical_history = models.ForeignKey(MedicalHistory, on_delete=models.CASCADE)
    pediatric_details = models.ForeignKey(PediatricDetails, on_delete=models.CASCADE)
    immunization_history = models.ForeignKey(ImmunizationHistory, on_delete=models.CASCADE, related_name='pediatric_immunization_history')
    doctor_order = models.ForeignKey(DoctorOrder, on_delete=models.CASCADE, null=True)
    nurse_notes = models.ForeignKey(NurseNotes, on_delete=models.CASCADE, null=True)
    vital_signs = models.ForeignKey(VitalSigns, on_delete=models.CASCADE, null=True)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)

class Child(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    economic_numbers = models.ForeignKey(EconomicNumbers, on_delete=models.CASCADE)
    child_details = models.ForeignKey(ChildDetails, on_delete=models.CASCADE)
    newborn_status = models.ForeignKey(NewbornStatus, on_delete=models.CASCADE)
    doctor_order = models.ForeignKey(DoctorOrder, on_delete=models.CASCADE, null=True)
    nurse_notes = models.ForeignKey(NurseNotes, on_delete=models.CASCADE, null=True)
    vital_signs = models.ForeignKey(VitalSigns, on_delete=models.CASCADE, null=True)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)

# Comment out models.py line 9 and models.py line 12 and forms.py lines 15-17 before adding superuser
# Uncomment after creating superuser account
    
# Create custom superuser manager to include birthdate as a required field




