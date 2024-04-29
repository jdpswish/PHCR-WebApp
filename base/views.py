from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.template.loader import get_template
from .models import User, UserProfile, EconomicNumbers, SocialHistory, MedicalHistory, Adult, Child,  Form, Pediatric, ImmunizationHistory, PediatricDetails, ChildDetails, NewbornStatus, DoctorOrder, NurseNotes, VitalSigns,Announcement
from .forms import RegistrationForm, UserProfileForm, EconomicNumbersForm, SocialHistoryForm, MedicalHistoryForm,  ChildDetailsForm, NewbornStatusForm, PediatricDetailsForm, ImmunizationHistoryForm, DoctorOrderForm, NurseNotesForm, VitalSignsForm, AnnouncementForm
from functools import wraps
from xhtml2pdf import pisa
from datetime import datetime, timedelta
from django.db.models import Q 

# Home
def home(request):
    last_announcement = Announcement.objects.last()
    context = {'last_announcement': last_announcement}
    return render(request, 'base/home.html', context)


# Authentication Functions
def register_page(request):
    if not request.user.is_authenticated:
        form = RegistrationForm()
        context = {'form': form}

        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                login(request, user)
                return redirect('user_dashboard')
            else: 
                # Add form errors to context
                context['form'] = form
                # Display form errors as messages
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")

        return render(request, 'base/register.html', context)
    else:
        return redirect('home')

def login_page(request):
    if not request.user.is_authenticated:
        context = {}
        if request.method == "POST":
            username = request.POST.get('username').lower()
            password = request.POST.get('password')
            
            # Check if Username exists
            if not User.objects.filter(username=username).exists():
                messages.error(request, 'Invalid Username')
                return redirect('login')
            
            # Authenticate 
            user = authenticate(request, username=username, password=password)
            
            # If user was returned, login. Otherwise, invalid password
            if user is not None:
                login(request, user)
                if request.user.is_staff:
                    return redirect('staff_dashboard')
                else:
                    return redirect('user_dashboard')
            else: 
                messages.error(request, "Invalid Password")
                return redirect('login')
            
        return render(request, 'base/login.html', context)
    else:
        # redirect to home if already authenticated
        return redirect('home')

def logout_client(request):
    logout(request)
    return redirect('home')

# PATIENT VIEW

@login_required(login_url='home')
def user_dashboard(request):
    user = User.objects.get(id=request.user.id)   
    user_profile = UserProfile.objects.filter(user=user).last()
    economic_numbers = EconomicNumbers.objects.filter(user=user).last()
    context = {
        'user': user,
        'user_profile': user_profile,
        'economic_numbers': economic_numbers,
        user: 'user'
    }
    return render(request, 'base/user_dashboard.html', context)

@login_required(login_url='login')
def patient_profile(request):
    user = request.user
    user_profile = UserProfile.objects.filter(user=user).last()
    economic_numbers = EconomicNumbers.objects.filter(user=user).last()
    context = {
        'user': user,
        'user_profile': user_profile,
        'economic_numbers': economic_numbers,
    }

    return render(request, 'base/patient-section/patient_profile.html', context)

@login_required(login_url='login')
def patient_record(request):
    user = request.user
    forms = Form.objects.filter(user=user)
    context = {'forms': forms}
    return render(request, 'base/patient-section/patient_record.html', context)

def data_privacy(request):
    if request.method == 'POST':
        if request.POST.get('acceptTerms') == 'accept':
            return redirect('choose_form')
        elif request.POST.get('acceptTerms') == 'decline':
            return redirect('user_dashboard')
    return render(request, 'base/patient-section/data_privacy.html')

# STAFF DASHBOARD

def staff_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')  
        elif not request.user.is_staff:
            return redirect('home')  
        else:
            return view_func(request, *args, **kwargs)
    return wrapper

@staff_login_required
def staff_dashboard(request):
    total_users = User.objects.count()
    total_patients = User.objects.filter(is_staff=False).count()
    total_staffs = User.objects.filter(is_staff=True, is_superuser=False).count()
    pending_forms_count = Form.objects.filter(status='Unverified').count()
    inactive_users_count = User.objects.filter(is_active=False).count()
    submitted_forms_count = Form.objects.filter(status='Verified').count()

    today = datetime.today()
    one_year_ago = today - timedelta(days=365)
    child_patients = User.objects.filter(
        Q(is_staff=False) & Q(birth_date__gte=one_year_ago)
    ).count()
    pediatric_patients = User.objects.filter(
        Q(is_staff=False) & Q(birth_date__lt=one_year_ago) & Q(birth_date__gte=today - timedelta(days=365*19))
    ).count()
    adult_patients = User.objects.filter(
        Q(is_staff=False) & Q(birth_date__lt=today - timedelta(days=365*19))
    ).count()

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  
    else:
        form = AnnouncementForm()

    context = {
        'total_users': total_users,
        'total_patients': total_patients,
        'total_staffs': total_staffs,
        'pending_forms_count': pending_forms_count,
        'inactive_users_count': inactive_users_count,
        'submitted_forms_count': submitted_forms_count,
        'child_patients': child_patients,
        'pediatric_patients': pediatric_patients,
        'adult_patients': adult_patients,
        'form': form,
    }

    return render(request, 'base/staff_dashboard.html', context)

@staff_login_required
def dashboard(request):
    total_users = User.objects.count()
    total_patients = User.objects.filter(is_staff=False).count()
    total_staffs = User.objects.filter(is_staff=True, is_superuser=False).count()
    pending_forms_count = Form.objects.filter(status='Unverified').count()
    inactive_users_count = User.objects.filter(is_active=False).count()
    submitted_forms_count = Form.objects.filter(status='Verified').count()

    # Calculate age groups of patients
    today = datetime.today()
    one_year_ago = today - timedelta(days=365)
    child_patients = User.objects.filter(
        Q(is_staff=False) & Q(birth_date__gte=one_year_ago)
    ).count()
    pediatric_patients = User.objects.filter(
        Q(is_staff=False) & Q(birth_date__lt=one_year_ago) & Q(birth_date__gte=today - timedelta(days=365*19))
    ).count()
    adult_patients = User.objects.filter(
        Q(is_staff=False) & Q(birth_date__lt=today - timedelta(days=365*19))
    ).count()

    context = {
        'total_users': total_users,
        'total_patients': total_patients,
        'total_staffs': total_staffs,
        'pending_forms_count': pending_forms_count,
        'inactive_users_count': inactive_users_count,
        'submitted_forms_count': submitted_forms_count,
        'child_patients': child_patients,
        'pediatric_patients': pediatric_patients,
        'adult_patients': adult_patients,
    }
    return render(request, 'base/staff-section/dashboard.html', context)


@staff_login_required
def unverifiedforms(request):
    unverified_forms = Form.objects.filter(status='Unverified')
    context = {'unverified_forms': unverified_forms}
    return render(request, 'base/staff-section/unverifiedforms.html', context)


@staff_login_required
def view_records(request):
    verified_forms = Form.objects.filter(status='Verified').order_by('-datetime_created')

    verified_forms_data = []
    for form in verified_forms:
        if form.record_type == 'Adult':
            patient_data = Adult.objects.filter(form=form).first()
            if patient_data:
                patient_name = f"{patient_data.user.first_name} {patient_data.user.last_name}"
                verified_forms_data.append({
                    'id': patient_data.id,
                    'patient_name': patient_name,
                    'record_type': form.record_type,
                    'birthdate': patient_data.user.birth_date,
                    'form_id': form.id,
                })
        elif form.record_type == 'Child':
            patient_data = Child.objects.filter(form=form).first()
            if patient_data:
                patient_name = f"{patient_data.user.first_name} {patient_data.user.last_name}"
                verified_forms_data.append({
                    'id': patient_data.id,
                    'patient_name': patient_name,
                    'record_type': form.record_type,
                    'birthdate': patient_data.user.birth_date,
                    'form_id': form.id,
                })
        elif form.record_type == 'Pediatric':
            patient_data = Pediatric.objects.filter(form=form).first()
            if patient_data:
                patient_name = f"{patient_data.user.first_name} {patient_data.user.last_name}"
                verified_forms_data.append({
                    'id': patient_data.id,
                    'patient_name': patient_name,
                    'record_type': form.record_type,
                    'birthdate': patient_data.user.birth_date,
                    'form_id': form.id,
                })

    context = {'verified_forms_data': verified_forms_data}
    return render(request, 'base/staff-section/view_precords.html', context)

@staff_login_required
def search_records(request):
    search_query = request.GET.get('search_query')
    verified_forms = Form.objects.filter(status='Verified').order_by('-datetime_created')

    verified_forms_data = []
    for form in verified_forms:
        if form.record_type == 'Adult':
            patient_data = Adult.objects.filter(form=form).first()
            if patient_data:
                patient_name = f"{patient_data.user.first_name} {patient_data.user.last_name}"
                verified_forms_data.append({
                    'id': patient_data.id,
                    'patient_name': patient_name,
                    'record_type': form.record_type,
                    'birthdate': patient_data.user.birth_date,
                    'form_id': form.id,
                })
        elif form.record_type == 'Child':
            patient_data = Child.objects.filter(form=form).first()
            if patient_data:
                patient_name = f"{patient_data.user.first_name} {patient_data.user.last_name}"
                verified_forms_data.append({
                    'id': patient_data.id,
                    'patient_name': patient_name,
                    'record_type': form.record_type,
                    'birthdate': patient_data.user.birth_date,
                    'form_id': form.id,
                })
        elif form.record_type == 'Pediatric':
            patient_data = Pediatric.objects.filter(form=form).first()
            if patient_data:
                patient_name = f"{patient_data.user.first_name} {patient_data.user.last_name}"
                verified_forms_data.append({
                    'id': patient_data.id,
                    'patient_name': patient_name,
                    'record_type': form.record_type,
                    'birthdate': patient_data.user.birth_date,
                    'form_id': form.id,
                })

    if search_query:
        verified_forms_data = [data for data in verified_forms_data if search_query.lower() in data['patient_name'].lower()]

    context = {'verified_forms_data': verified_forms_data, 'search_query': search_query}
    return render(request, 'base/staff-section/search_records.html', context)


@staff_login_required
def manage_users(request):
    search_query = request.GET.get('search_query')
    patients = User.objects.filter(is_staff=False, is_active=True)
    
    if search_query:
        patients = patients.filter(
            first_name__icontains=search_query
        ) | patients.filter(
            last_name__icontains=search_query
        )
    
    context = {'patients': patients}
    return render(request, 'base/staff-section/manage_users.html', context)

@staff_login_required
def search_users(request):
    search_query = request.GET.get('search_query')
    patients = User.objects.filter(is_staff=False, is_active=True)
    
    if search_query:
        patients = patients.filter(
            first_name__icontains=search_query
        ) | patients.filter(
            last_name__icontains=search_query
        )
    
    context = {'patients': patients}
    return render(request, 'base/staff-section/search_users.html', context)

@staff_login_required
def learn_more(request):
    context = {}
    return render(request, 'base/staff-section/learn_more.html', context)


#PATIENT FORMS

@login_required(login_url='data_privacy')
def choose_form_view(request):
    return render(request, 'base/patient-section/choose_form.html')

@login_required(login_url='login')
def child_form(request):

    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST)
        economic_numbers_form = EconomicNumbersForm(request.POST)
        child_details_form = ChildDetailsForm(request.POST)
        newborn_status_form = NewbornStatusForm(request.POST)

        if all(form.is_valid() for form in [user_profile_form, economic_numbers_form, child_details_form, newborn_status_form]):
            
            user_profile = user_profile_form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            economic_numbers = economic_numbers_form.save(commit=False)
            economic_numbers.user = request.user
            economic_numbers.save()

            child_details = child_details_form.save(commit=False)
            child_details.user = request.user
            child_details.save()

            newborn_status = newborn_status_form.save(commit=False)
            newborn_status.user = request.user
            newborn_status.save()

            doctor_order = None 
            nurse_notes = None 
            vital_signs = None

            form_instance = Form.objects.create(
                user=request.user,
                title="Child Form",
                record_type="Child",
                status="Unverified"  
            )

            child_patient = Child.objects.update_or_create(
                user=request.user,
                user_profile=user_profile,
                economic_numbers=economic_numbers,
                child_details=child_details,
                newborn_status=newborn_status,
                doctor_order = doctor_order,
                nurse_notes = nurse_notes,
                vital_signs = vital_signs,
                form=form_instance
            )

            return redirect('user_dashboard')

    else:
        user_profile_form = UserProfileForm()
        economic_numbers_form = EconomicNumbersForm()
        child_details_form = ChildDetailsForm()
        newborn_status_form = NewbornStatusForm()

    context = {
        'user_profile_form': user_profile_form,
        'economic_numbers_form': economic_numbers_form,
        'child_details_form': child_details_form,
        'newborn_status_form': newborn_status_form,
    }

    return render(request, 'base/patient-section/child_form.html', context)

@login_required(login_url='login')
def pediatric_form(request):

    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST)
        economic_numbers_form = EconomicNumbersForm(request.POST)
        social_history_form = SocialHistoryForm(request.POST)
        medical_history_form = MedicalHistoryForm(request.POST)
        pediatric_details_form = PediatricDetailsForm(request.POST)
        immunization_history_form = ImmunizationHistoryForm(request.POST)

        if all(form.is_valid() for form in [user_profile_form, economic_numbers_form, social_history_form, medical_history_form, pediatric_details_form, immunization_history_form]):
            
            user_profile = user_profile_form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            economic_numbers = economic_numbers_form.save(commit=False)
            economic_numbers.user = request.user
            economic_numbers.save()

            social_history = social_history_form.save(commit=False)
            social_history.user = request.user
            social_history.save()

            medical_history = medical_history_form.save(commit=False)
            medical_history.user = request.user
            medical_history.save()

            pediatric_details = pediatric_details_form.save(commit=False)
            pediatric_details.user = request.user
            pediatric_details.save()

            immunization_history = immunization_history_form.save(commit=False)
            immunization_history.user = request.user
            immunization_history.save()

            doctor_order = None 
            nurse_notes = None 
            vital_signs = None

            form_instance = Form.objects.create(
                user=request.user,
                title="Pediatric Form",
                record_type="Pediatric",
                status="Unverified"  
            )

            pediatric_patient = Pediatric.objects.create(
                user=request.user,
                user_profile=user_profile,
                economic_numbers=economic_numbers,
                social_history=social_history,
                medical_history=medical_history,
                pediatric_details=pediatric_details,
                immunization_history=immunization_history,
                doctor_order = doctor_order,
                nurse_notes = nurse_notes,
                vital_signs = vital_signs,
                form=form_instance

            )

            return redirect('user_dashboard')

    else:
        user_profile_form = UserProfileForm()
        economic_numbers_form = EconomicNumbersForm()
        social_history_form = SocialHistoryForm()
        medical_history_form = MedicalHistoryForm()
        pediatric_details_form = PediatricDetailsForm()
        immunization_history_form = ImmunizationHistoryForm()

    context = {
        'user_profile_form': user_profile_form,
        'economic_numbers_form': economic_numbers_form,
        'social_history_form': social_history_form,
        'medical_history_form': medical_history_form,
        'pediatric_details_form': pediatric_details_form,
        'immunization_history_form': immunization_history_form,
    }

    return render(request, 'base/patient-section/pediatric_form.html', context)

@login_required(login_url='login')
def adult_form(request):

    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST)
        economic_numbers_form = EconomicNumbersForm(request.POST)
        social_history_form = SocialHistoryForm(request.POST)
        medical_history_form = MedicalHistoryForm(request.POST)

        if all(form.is_valid() for form in [user_profile_form, economic_numbers_form, social_history_form, medical_history_form]):
            
            user_profile = user_profile_form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            economic_numbers = economic_numbers_form.save(commit=False)
            economic_numbers.user = request.user
            economic_numbers.save()

            social_history = social_history_form.save(commit=False)
            social_history.user = request.user
            social_history.save()

            medical_history = medical_history_form.save(commit=False)
            medical_history.user = request.user
            medical_history.save()

            doctor_order = None 
            nurse_notes = None 
            vital_signs = None

            form_instance = Form.objects.create(
                user=request.user,
                title="Adult Form",
                record_type="Adult",
                status="Unverified"  
            )

            adult_patient = Adult.objects.create(
                user=request.user,
                user_profile=user_profile,
                economic_numbers=economic_numbers,
                social_history=social_history,
                medical_history=medical_history,
                doctor_order = doctor_order,
                nurse_notes = nurse_notes,
                vital_signs = vital_signs,
                form=form_instance
            )

            return redirect('user_dashboard')

    else:
        user_profile_form = UserProfileForm()
        economic_numbers_form = EconomicNumbersForm()
        social_history_form = SocialHistoryForm()
        medical_history_form = MedicalHistoryForm()

    context = {
        'user_profile_form': user_profile_form,
        'economic_numbers_form': economic_numbers_form,
        'social_history_form': social_history_form,
        'medical_history_form': medical_history_form,
    }

    return render(request, 'base/patient-section/adult_form.html', context)


@login_required(login_url='login')
def add_doctor_order(request, form_id):
    form_instance = get_object_or_404(Form, pk=form_id)
    if DoctorOrder.objects.filter(id=form_id).exists():
        existing_order = get_object_or_404(DoctorOrder, id=form_id)
        doctor_order_form = DoctorOrderForm(request.POST or None, instance=existing_order)
    else:
        doctor_order_form = DoctorOrderForm(request.POST or None)
    
    if request.method == 'POST':
        if doctor_order_form.is_valid():
            doctor_order = doctor_order_form.save(commit=False)
            doctor_order.user = form_instance.user
            doctor_order.filled_by = request.user
            doctor_order.save()
            
            form_instance.doctor_order = doctor_order
            form_instance.save()
            
            if form_instance.record_type == 'Adult':
                patient_instance = get_object_or_404(Adult, form=form_instance)
                patient_instance.doctor_order = doctor_order
                patient_instance.save()
            elif form_instance.record_type == 'Pediatric':
                patient_instance = get_object_or_404(Pediatric, form=form_instance)
                patient_instance.doctor_order = doctor_order
                patient_instance.save()
            elif form_instance.record_type == 'Child':
                patient_instance = get_object_or_404(Child, form=form_instance)
                patient_instance.doctor_order = doctor_order
                patient_instance.save()
            
            return redirect('staff_dashboard')  
    
    return render(request, 'base/staff-section/add_doctor_order.html', {'doctor_order_form': doctor_order_form})

# Nurse Notes View
@staff_login_required
def add_nurse_notes(request, form_id):
    form_instance = get_object_or_404(Form, pk=form_id)
    
    if NurseNotes.objects.filter(id=form_id).exists():
        existing_notes = get_object_or_404(NurseNotes, id=form_id)
        existing_vital_signs = get_object_or_404(VitalSigns, id=form_id)
        nurse_notes_form = NurseNotesForm(request.POST or None, instance=existing_notes)
        vital_signs_form = VitalSignsForm(request.POST or None, instance=existing_vital_signs)
    else:
        nurse_notes_form = NurseNotesForm(request.POST or None)
        vital_signs_form = VitalSignsForm(request.POST or None)
    
    if request.method == 'POST':
        if nurse_notes_form.is_valid() and vital_signs_form.is_valid():
            nurse_notes = nurse_notes_form.save(commit=False)
            nurse_notes.user = form_instance.user
            nurse_notes.filled_by = request.user
            nurse_notes.save()
            
            vital_signs = vital_signs_form.save(commit=False)
            vital_signs.user = form_instance.user
            vital_signs.filled_by = request.user
            vital_signs.save()
            
            form_instance.nurse_notes = nurse_notes
            form_instance.vital_signs = vital_signs
            form_instance.save()
            
            if form_instance.record_type == 'Adult':
                patient_instance = get_object_or_404(Adult, form=form_instance)
                patient_instance.nurse_notes = nurse_notes
                patient_instance.vital_signs = vital_signs
                patient_instance.save()
            elif form_instance.record_type == 'Pediatric':
                patient_instance = get_object_or_404(Pediatric, form=form_instance)
                patient_instance.nurse_notes = nurse_notes
                patient_instance.vital_signs = vital_signs
                patient_instance.save()
            elif form_instance.record_type == 'Child':
                patient_instance = get_object_or_404(Child, form=form_instance)
                patient_instance.nurse_notes = nurse_notes
                patient_instance.vital_signs = vital_signs
                patient_instance.save()
            
            return redirect('staff_dashboard')  
    
    return render(request, 'base/staff-section/add_nurse_notes.html', {'nurse_notes_form': nurse_notes_form, 'vital_signs_form': vital_signs_form})


#PATIENT CRUD
@login_required(login_url='home')
def patient_view_form(request, form_id):
    user = request.user
    form = Form.objects.get(pk=form_id, user=user)

    if form.record_type == 'Adult':
        adult = Adult.objects.get(form=form, user=user)
        user_profile = adult.user_profile
        economic_numbers = adult.economic_numbers
        social_history = adult.social_history
        medical_history = adult.medical_history
        doctor_order = adult.doctor_order
        nurse_notes = adult.nurse_notes
        vital_signs = adult.vital_signs

        context = {
            'form': form,
            'user_profile': user_profile,
            'economic_numbers': economic_numbers,
            'social_history': social_history,
            'medical_history': medical_history,
            'doctor_order': doctor_order,
            'nurse_notes' : nurse_notes,
            'vital_signs': vital_signs
        }

    elif form.record_type == 'Child':
        child = get_object_or_404(Child, form=form, user=user)
        user_profile = child.user_profile
        child_details = child.child_details
        newborn_status = child.newborn_status
        economic_numbers = child.economic_numbers
        doctor_order = child.doctor_order
        nurse_notes = child.nurse_notes
        vital_signs = child.vital_signs

        context = {
            'form': form,
            'user_profile': user_profile,
            'child_details': child_details,
            'newborn_status': newborn_status,
            'economic_numbers': economic_numbers,
            'doctor_order': doctor_order,
            'nurse_notes' : nurse_notes,
            'vital_signs': vital_signs
        }

    elif form.record_type == 'Pediatric':
        pediatric = get_object_or_404(Pediatric, form=form, user=user)
        user_profile = pediatric.user_profile
        pediatric_details = pediatric.pediatric_details
        immunization_history = pediatric.immunization_history
        social_history = pediatric.social_history
        medical_history = pediatric.medical_history
        economic_numbers = pediatric.economic_numbers
        doctor_order = pediatric.doctor_order
        nurse_notes = pediatric.nurse_notes
        vital_signs = pediatric.vital_signs

        context = {
            'form': form,
            'user_profile': user_profile,
            'pediatric_details': pediatric_details,
            'immunization_history': immunization_history,
            'social_history': social_history,
            'medical_history': medical_history,
            'economic_numbers': economic_numbers,
            'doctor_order': doctor_order,
            'nurse_notes' : nurse_notes,
            'vital_signs': vital_signs
        }

    return render(request, 'base/patient-section/patient_view_form.html', context)



@login_required(login_url='home')
def patient_update_form(request, form_id):
    user = request.user
    form = get_object_or_404(Form, pk=form_id, user=user)

    if form.record_type == 'Adult':
        adult = get_object_or_404(Adult, form=form, user=user)
        user_profile = adult.user_profile
        economic_numbers = adult.economic_numbers
        social_history = adult.social_history
        medical_history = adult.medical_history

        if request.method == 'POST':
            user_profile_form = UserProfileForm(request.POST, instance=user_profile)
            economic_numbers_form = EconomicNumbersForm(request.POST, instance=economic_numbers)
            social_history_form = SocialHistoryForm(request.POST, instance=social_history)
            medical_history_form = MedicalHistoryForm(request.POST, instance=medical_history)

            if all(form.is_valid() for form in [user_profile_form, economic_numbers_form, social_history_form, medical_history_form]):
                user_profile_form.save()
                economic_numbers_form.save()
                social_history_form.save()
                medical_history_form.save()
                return redirect('patient_view_form', form_id=form_id)
        else:
            user_profile_form = UserProfileForm(instance=user_profile)
            economic_numbers_form = EconomicNumbersForm(instance=economic_numbers)
            social_history_form = SocialHistoryForm(instance=social_history)
            medical_history_form = MedicalHistoryForm(instance=medical_history)

        context = {
            'form': form,
            'user_profile_form': user_profile_form,
            'economic_numbers_form': economic_numbers_form,
            'social_history_form': social_history_form,
            'medical_history_form': medical_history_form,
        }

        return render(request, 'base/patient-section/patient_update_form.html', context)

    elif form.record_type == 'Child':
        child = get_object_or_404(Child, form=form, user=user)
        user_profile = child.user_profile
        child_details = child.child_details
        newborn_status = child.newborn_status
        economic_numbers = child.economic_numbers

        if request.method == 'POST':
            user_profile_form = UserProfileForm(request.POST, instance=user_profile)
            child_details_form = ChildDetailsForm(request.POST, instance=child_details)
            newborn_status_form = NewbornStatusForm(request.POST, instance=newborn_status)
            economic_numbers_form = EconomicNumbersForm(request.POST, instance=economic_numbers)

            if all(form.is_valid() for form in [user_profile_form, child_details_form, newborn_status_form, economic_numbers_form]):
                user_profile_form.save()
                child_details_form.save()
                newborn_status_form.save()
                economic_numbers_form.save()
                return redirect('patient_view_form', form_id=form_id)
        else:
            user_profile_form = UserProfileForm(instance=user_profile)
            child_details_form = ChildDetailsForm(instance=child_details)
            newborn_status_form = NewbornStatusForm(instance=newborn_status)
            economic_numbers_form = EconomicNumbersForm(instance=economic_numbers)

        context = {
            'form': form,
            'user_profile_form': user_profile_form,
            'child_details_form': child_details_form,
            'newborn_status_form': newborn_status_form,
            'economic_numbers_form': economic_numbers_form,
        }

        return render(request, 'base/patient-section/patient_update_form.html', context)

    elif form.record_type == 'Pediatric':
        pediatric = get_object_or_404(Pediatric, form=form, user=user)
        user_profile = pediatric.user_profile
        pediatric_details = pediatric.pediatric_details
        immunization_history = pediatric.immunization_history
        social_history = pediatric.social_history
        medical_history = pediatric.medical_history
        economic_numbers = pediatric.economic_numbers

        if request.method == 'POST':
            user_profile_form = UserProfileForm(request.POST, instance=user_profile)
            pediatric_details_form = PediatricDetailsForm(request.POST, instance=pediatric_details)
            immunization_history_form = ImmunizationHistoryForm(request.POST, instance=immunization_history)
            social_history_form = SocialHistoryForm(request.POST, instance=social_history)
            medical_history_form = MedicalHistoryForm(request.POST, instance=medical_history)
            economic_numbers_form = EconomicNumbersForm(request.POST, instance=economic_numbers)

            if all(form.is_valid() for form in [user_profile_form, pediatric_details_form, immunization_history_form, social_history_form, medical_history_form, economic_numbers_form]):
                user_profile_form.save()
                pediatric_details_form.save()
                immunization_history_form.save()
                social_history_form.save()
                medical_history_form.save()
                economic_numbers_form.save()
                return redirect('patient_view_form', form_id=form_id)
        else:
            user_profile_form = UserProfileForm(instance=user_profile)
            pediatric_details_form = PediatricDetailsForm(instance=pediatric_details)
            immunization_history_form = ImmunizationHistoryForm(instance=immunization_history)
            social_history_form = SocialHistoryForm(instance=social_history)
            medical_history_form = MedicalHistoryForm(instance=medical_history)
            economic_numbers_form = EconomicNumbersForm(instance=economic_numbers)

        context = {
            'form': form,
            'user_profile_form': user_profile_form,
            'pediatric_details_form': pediatric_details_form,
            'immunization_history_form': immunization_history_form,
            'social_history_form': social_history_form,
            'medical_history_form': medical_history_form,
            'economic_numbers_form': economic_numbers_form,
        }

        return render(request, 'base/patient-section/patient_update_form.html', context)
    
@login_required(login_url='home')
def patient_delete_form(request, form_id):
    user = request.user
    form = get_object_or_404(Form, pk=form_id, user=user)

    if form.record_type == 'Adult':
        adult = get_object_or_404(Adult, form=form, user=user)
        adult.user_profile.delete()
        adult.economic_numbers.delete()
        adult.social_history.delete()
        adult.medical_history.delete()
        adult.delete()
    elif form.record_type == 'Child':
        child = get_object_or_404(Child, form=form, user=user)
        child.user_profile.delete()
        child.economic_numbers.delete()
        child.child_details.delete()
        child.newborn_status.delete()
        child.delete()
    elif form.record_type == 'Pediatric':
        pediatric = get_object_or_404(Pediatric, form=form, user=user)
        pediatric.user_profile.delete()
        pediatric.economic_numbers.delete()
        pediatric.social_history.delete()
        pediatric.medical_history.delete()
        pediatric.pediatric_details.delete()
        pediatric.immunization_history.delete()
        pediatric.delete()

    form.delete()

    return redirect('user_dashboard')

@login_required(login_url='home')
def generate_pdf(request, form_id):
    form = get_object_or_404(Form, pk=form_id)
    user = request.user

    if form.record_type == 'Adult':
        adult = get_object_or_404(Adult, form=form, user=user)
        user_profile = adult.user_profile
        economic_numbers = adult.economic_numbers
        social_history = adult.social_history
        medical_history = adult.medical_history

        context = {
            'form': form,
            'user_profile': user_profile,
            'economic_numbers': economic_numbers,
            'social_history': social_history,
            'medical_history': medical_history,
        }

    elif form.record_type == 'Child':
        child = get_object_or_404(Child, form=form, user=user)
        user_profile = child.user_profile
        child_details = child.child_details
        newborn_status = child.newborn_status
        economic_numbers = child.economic_numbers

        context = {
            'form': form,
            'user_profile': user_profile,
            'child_details': child_details,
            'newborn_status': newborn_status,
            'economic_numbers': economic_numbers,
        }

    elif form.record_type == 'Pediatric':
        pediatric = get_object_or_404(Pediatric, form=form, user=user)
        user_profile = pediatric.user_profile
        pediatric_details = pediatric.pediatric_details
        immunization_history = pediatric.immunization_history
        social_history = pediatric.social_history
        medical_history = pediatric.medical_history
        economic_numbers = pediatric.economic_numbers

        context = {
            'form': form,
            'user_profile': user_profile,
            'pediatric_details': pediatric_details,
            'immunization_history': immunization_history,
            'social_history': social_history,
            'medical_history': medical_history,
            'economic_numbers': economic_numbers,
        }

    html_template = get_template('base/patient-section/patient_view_form.html')
    html = html_template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="HealthRecord_{form_id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('An error occurred while generating the PDF')

    return response

#STAFF CRUD

@staff_login_required
def staff_view_form(request, form_id):
   
    form = get_object_or_404(Form, pk=form_id)

    if form.record_type == 'Adult':
        adult = get_object_or_404(Adult, form=form)
        user_profile = adult.user_profile
        economic_numbers = adult.economic_numbers
        social_history = adult.social_history
        medical_history = adult.medical_history
        doctor_order = adult.doctor_order
        nurse_notes = adult.nurse_notes
        vital_signs = adult.vital_signs

        context = {
            'form': form,
            'user_profile': user_profile,
            'economic_numbers': economic_numbers,
            'social_history': social_history,
            'medical_history': medical_history,
            'doctor_order': doctor_order,
            'nurse_notes' : nurse_notes,
            'vital_signs': vital_signs
        }

    elif form.record_type == 'Child':
        child = get_object_or_404(Child, form=form)
        user_profile = child.user_profile
        child_details = child.child_details
        newborn_status = child.newborn_status
        economic_numbers = child.economic_numbers
        doctor_order = child.doctor_order
        nurse_notes = child.nurse_notes
        vital_signs = child.vital_signs

        context = {
            'form': form,
            'user_profile': user_profile,
            'child_details': child_details,
            'newborn_status': newborn_status,
            'economic_numbers': economic_numbers,
            'doctor_order': doctor_order,
            'nurse_notes' : nurse_notes,
            'vital_signs': vital_signs
        }

    elif form.record_type == 'Pediatric':
        pediatric = get_object_or_404(Pediatric, form=form)
        user_profile = pediatric.user_profile
        pediatric_details = pediatric.pediatric_details
        immunization_history = pediatric.immunization_history
        social_history = pediatric.social_history
        medical_history = pediatric.medical_history
        economic_numbers = pediatric.economic_numbers
        doctor_order = pediatric.doctor_order
        nurse_notes = pediatric.nurse_notes
        vital_signs = pediatric.vital_signs

        context = {
            'form': form,
            'user_profile': user_profile,
            'pediatric_details': pediatric_details,
            'immunization_history': immunization_history,
            'social_history': social_history,
            'medical_history': medical_history,
            'economic_numbers': economic_numbers,
            'doctor_order': doctor_order,
            'nurse_notes' : nurse_notes,
            'vital_signs': vital_signs
        }

    return render(request, 'base/patient-section/patient_view_form.html', context)

@staff_login_required
def staff_update_form(request, form_id):
    form = get_object_or_404(Form, pk=form_id)

    if form.record_type == 'Adult':
        adult = get_object_or_404(Adult, form=form)
        user_profile = adult.user_profile
        economic_numbers = adult.economic_numbers
        social_history = adult.social_history
        medical_history = adult.medical_history
        doctor_order = adult.doctor_order
        nurse_notes = adult.nurse_notes
        vital_signs = adult.vital_signs

        if request.method == 'POST':
            user_profile_form = UserProfileForm(request.POST, instance=user_profile)
            economic_numbers_form = EconomicNumbersForm(request.POST, instance=economic_numbers)
            social_history_form = SocialHistoryForm(request.POST, instance=social_history)
            medical_history_form = MedicalHistoryForm(request.POST, instance=medical_history)
            doctor_order_form = DoctorOrderForm(request.POST, instance=doctor_order)
            nurse_notes_form = NurseNotesForm(request.POST, instance=nurse_notes)
            vital_signs_form = VitalSignsForm(request.POST, instance=vital_signs)

            if all(form.is_valid() for form in [user_profile_form, economic_numbers_form, social_history_form, medical_history_form, doctor_order_form, nurse_notes_form, vital_signs_form]):
                user_profile_form.save()
                economic_numbers_form.save()
                social_history_form.save()
                medical_history_form.save()
                doctor_order_form.save()
                nurse_notes_form.save()
                vital_signs_form.save()
                return redirect('staff_view_form', form_id=form_id)
        else:
            user_profile_form = UserProfileForm(instance=user_profile)
            economic_numbers_form = EconomicNumbersForm(instance=economic_numbers)
            social_history_form = SocialHistoryForm(instance=social_history)
            medical_history_form = MedicalHistoryForm(instance=medical_history)
            doctor_order_form = DoctorOrderForm(instance=doctor_order)
            nurse_notes_form = NurseNotesForm(instance=nurse_notes)
            vital_signs_form = VitalSignsForm(instance=vital_signs)

        context = {
            'form': form,
            'user_profile_form': user_profile_form,
            'economic_numbers_form': economic_numbers_form,
            'social_history_form': social_history_form,
            'medical_history_form': medical_history_form,
            'doctor_order_form': doctor_order_form,
            'nurse_notes_form': nurse_notes_form,
            'vital_signs_form': vital_signs_form,
        }

        return render(request, 'base/patient-section/patient_update_form.html', context)

    elif form.record_type == 'Child':
        child = get_object_or_404(Child, form=form)
        user_profile = child.user_profile
        child_details = child.child_details
        newborn_status = child.newborn_status
        economic_numbers = child.economic_numbers
        doctor_order = child.doctor_order
        nurse_notes = child.nurse_notes
        vital_signs = child.vital_signs

        if request.method == 'POST':
            user_profile_form = UserProfileForm(request.POST, instance=user_profile)
            child_details_form = ChildDetailsForm(request.POST, instance=child_details)
            newborn_status_form = NewbornStatusForm(request.POST, instance=newborn_status)
            economic_numbers_form = EconomicNumbersForm(request.POST, instance=economic_numbers)
            doctor_order_form = DoctorOrderForm(request.POST, instance=doctor_order)
            nurse_notes_form = NurseNotesForm(request.POST, instance=nurse_notes)
            vital_signs_form = VitalSignsForm(request.POST, instance=vital_signs)

            if all(form.is_valid() for form in [user_profile_form, child_details_form, newborn_status_form, economic_numbers_form, doctor_order_form, nurse_notes_form, vital_signs_form]):
                user_profile_form.save()
                child_details_form.save()
                newborn_status_form.save()
                economic_numbers_form.save()
                doctor_order_form.save()
                nurse_notes_form.save()
                vital_signs_form.save()
                return redirect('staff_view_form', form_id=form_id)
        else:
            user_profile_form = UserProfileForm(instance=user_profile)
            child_details_form = ChildDetailsForm(instance=child_details)
            newborn_status_form = NewbornStatusForm(instance=newborn_status)
            economic_numbers_form = EconomicNumbersForm(instance=economic_numbers)
            doctor_order_form = DoctorOrderForm(instance=doctor_order)
            nurse_notes_form = NurseNotesForm(instance=nurse_notes)
            vital_signs_form = VitalSignsForm(instance=vital_signs)

        context = {
            'form': form,
            'user_profile_form': user_profile_form,
            'child_details_form': child_details_form,
            'newborn_status_form': newborn_status_form,
            'economic_numbers_form': economic_numbers_form,
            'doctor_order_form': doctor_order_form,
            'nurse_notes_form': nurse_notes_form,
            'vital_signs_form': vital_signs_form,
        }

        return render(request, 'base/patient-section/patient_update_form.html', context)

    elif form.record_type == 'Pediatric':
        pediatric = get_object_or_404(Pediatric, form=form)
        user_profile = pediatric.user_profile
        pediatric_details = pediatric.pediatric_details
        immunization_history = pediatric.immunization_history
        social_history = pediatric.social_history
        medical_history = pediatric.medical_history
        economic_numbers = pediatric.economic_numbers
        doctor_order = pediatric.doctor_order
        nurse_notes = pediatric.nurse_notes
        vital_signs = pediatric.vital_signs

        if request.method == 'POST':
            user_profile_form = UserProfileForm(request.POST, instance=user_profile)
            pediatric_details_form = PediatricDetailsForm(request.POST, instance=pediatric_details)
            immunization_history_form = ImmunizationHistoryForm(request.POST, instance=immunization_history)
            social_history_form = SocialHistoryForm(request.POST, instance=social_history)
            medical_history_form = MedicalHistoryForm(request.POST, instance=medical_history)
            economic_numbers_form = EconomicNumbersForm(request.POST, instance=economic_numbers)
            doctor_order_form = DoctorOrderForm(request.POST, instance=doctor_order)
            nurse_notes_form = NurseNotesForm(request.POST, instance=nurse_notes)
            vital_signs_form = VitalSignsForm(request.POST, instance=vital_signs)

            if all(form.is_valid() for form in [user_profile_form, pediatric_details_form, immunization_history_form, social_history_form, medical_history_form, economic_numbers_form, doctor_order_form, nurse_notes_form, vital_signs_form]):
                user_profile_form.save()
                pediatric_details_form.save()
                immunization_history_form.save()
                social_history_form.save()
                medical_history_form.save()
                economic_numbers_form.save()
                doctor_order_form.save()
                nurse_notes_form.save()
                vital_signs_form.save()
                return redirect('staff_view_form', form_id=form_id)
        else:
            user_profile_form = UserProfileForm(instance=user_profile)
            pediatric_details_form = PediatricDetailsForm(instance=pediatric_details)
            immunization_history_form = ImmunizationHistoryForm(instance=immunization_history)
            social_history_form = SocialHistoryForm(instance=social_history)
            medical_history_form = MedicalHistoryForm(instance=medical_history)
            economic_numbers_form = EconomicNumbersForm(instance=economic_numbers)
            doctor_order_form = DoctorOrderForm(instance=doctor_order)
            nurse_notes_form = NurseNotesForm(instance=nurse_notes)
            vital_signs_form = VitalSignsForm(instance=vital_signs)

        context = {
            'form': form,
            'user_profile_form': user_profile_form,
            'pediatric_details_form': pediatric_details_form,
            'immunization_history_form': immunization_history_form,
            'social_history_form': social_history_form,
            'medical_history_form': medical_history_form,
            'economic_numbers_form': economic_numbers_form,
            'doctor_order_form': doctor_order_form,
            'nurse_notes_form': nurse_notes_form,
            'vital_signs_form': vital_signs_form,
        }

        return render(request, 'base/patient-section/patient_update_form.html', context)

    
@staff_login_required
def staff_delete_form(request, form_id):
    form = get_object_or_404(Form, pk=form_id)

    if form.record_type == 'Adult':
        adult = get_object_or_404(Adult, form=form)
        adult.user_profile.delete()
        adult.economic_numbers.delete()
        adult.social_history.delete()
        adult.medical_history.delete()
        adult.doctor_order.delete()
        adult.nurse_notes.delete()
        adult.vital_signs.delete()
        adult.delete()
    elif form.record_type == 'Child':
        child = get_object_or_404(Child, form=form)
        child.user_profile.delete()
        child.economic_numbers.delete()
        child.child_details.delete()
        child.newborn_status.delete()
        child.doctor_order.delete()
        child.nurse_notes.delete()
        child.vital_signs.delete()
        child.delete()
    elif form.record_type == 'Pediatric':
        pediatric = get_object_or_404(Pediatric, form=form)
        pediatric.user_profile.delete()
        pediatric.economic_numbers.delete()
        pediatric.social_history.delete()
        pediatric.medical_history.delete()
        pediatric.pediatric_details.delete()
        pediatric.immunization_history.delete()
        pediatric.doctor_order.delete()
        pediatric.nurse_notes.delete()
        pediatric.vital_signs.delete()
        pediatric.delete()

    form.delete()

    return redirect('staff_dashboard')

@staff_login_required
def staff_accept_form(request, form_id):
    form = get_object_or_404(Form, pk=form_id)
    form.status = 'Verified'
    form.save()
    return HttpResponse('The Form is successfully verified.')

@staff_login_required
def staff_view_profile(request, user_id):
    user = User.objects.get(pk=user_id)
    user_profile = UserProfile.objects.filter(user=user).last()
    economic_numbers = EconomicNumbers.objects.filter(user=user).last()

    context = {
        'user': user,
        'user_profile': user_profile,
        'economic_numbers': economic_numbers,
    }

    return render(request, 'base/patient-section/patient_profile.html', context)

@staff_login_required
def staff_suspend_user(request, user_id):
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        user.is_active = False
        user.save()
        return HttpResponse("The user is suspended successfully.")
    else:
        context = {'user': user}
        return render(request, 'base/staff-section/suspend_user.html', context)

@staff_login_required
def staff_generate_pdf(request, form_id):
    form = get_object_or_404(Form, pk=form_id)

    if form.record_type == 'Adult':
        adult = get_object_or_404(Adult, form=form)
        user_profile = adult.user_profile
        economic_numbers = adult.economic_numbers
        social_history = adult.social_history
        medical_history = adult.medical_history

        context = {
            'form': form,
            'user_profile': user_profile,
            'economic_numbers': economic_numbers,
            'social_history': social_history,
            'medical_history': medical_history,
        }

    elif form.record_type == 'Child':
        child = get_object_or_404(Child, form=form)
        user_profile = child.user_profile
        child_details = child.child_details
        newborn_status = child.newborn_status
        economic_numbers = child.economic_numbers

        context = {
            'form': form,
            'user_profile': user_profile,
            'child_details': child_details,
            'newborn_status': newborn_status,
            'economic_numbers': economic_numbers,
        }

    elif form.record_type == 'Pediatric':
        pediatric = get_object_or_404(Pediatric, form=form)
        user_profile = pediatric.user_profile
        pediatric_details = pediatric.pediatric_details
        immunization_history = pediatric.immunization_history
        social_history = pediatric.social_history
        medical_history = pediatric.medical_history
        economic_numbers = pediatric.economic_numbers

        context = {
            'form': form,
            'user_profile': user_profile,
            'pediatric_details': pediatric_details,
            'immunization_history': immunization_history,
            'social_history': social_history,
            'medical_history': medical_history,
            'economic_numbers': economic_numbers,
        }

    html_template = get_template('base/patient-section/patient_view_form.html')
    html = html_template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="HealthRecord_{form_id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('An error occurred while generating the PDF')

    return response

@staff_login_required
def upload_photo(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  
    else:
        form = AnnouncementForm()
    return render(request, 'base/staff-section/upload_photo.html', {'form': form})

