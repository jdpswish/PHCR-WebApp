from django.shortcuts import render, redirect
from . .models import User, Adult, Child,  Form, Pediatric, MedicalHistory, SocialHistory
from . .forms import  AnnouncementForm
from functools import wraps
from datetime import datetime, timedelta
from django.db.models import Q 

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


def calculate_statistics():
    total_users = User.objects.count()
    total_patients = User.objects.filter(is_staff=False).count()
    total_staffs = User.objects.filter(is_staff=True, is_superuser=False).count()
    pending_forms_count = Form.objects.filter(status='Unverified').count()
    inactive_users_count = User.objects.filter(is_active=False).count()
    submitted_forms_count = Form.objects.filter(status='Verified').count()

    medical_conditions = {
        'diabetes': MedicalHistory.objects.filter(diabetes=True).count(),
        'asthma': MedicalHistory.objects.filter(asthma=True).count(),
        'hypertension': MedicalHistory.objects.filter(hypertension=True).count(),
        'pulmonary_tubercolosis': MedicalHistory.objects.filter(pulmonary_tubercolosis=True).count(),
        'cancer': MedicalHistory.objects.filter(cancer=True).count(),
        'cough_2_weeks': MedicalHistory.objects.filter(cough_2_weeks=True).count(),
    }

    social_habits = {
        'smoker': SocialHistory.objects.filter(smoker=True).count(),
        'alcohol_intake': SocialHistory.objects.filter(alcohol_intake=True).count(),
        'prohibited_drug': SocialHistory.objects.filter(prohibited_drug=True).count(),
    }

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

    return {
        'total_users': total_users,
        'total_patients': total_patients,
        'total_staffs': total_staffs,
        'pending_forms_count': pending_forms_count,
        'inactive_users_count': inactive_users_count,
        'submitted_forms_count': submitted_forms_count,
        'child_patients': child_patients,
        'pediatric_patients': pediatric_patients,
        'adult_patients': adult_patients,
        'medical_conditions': medical_conditions,
        'social_habits': social_habits,
    }


@staff_login_required
def staff_profile(request):
    user = request.user
    context = {
        'user': user,
    }

    return render(request, 'base/staff-section/staff_profile.html', context)


@staff_login_required
def staff_dashboard(request):
    context = calculate_statistics()
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  
    else:
        form = AnnouncementForm()
    context['form'] = form
    return render(request, 'base/staff_dashboard.html', context)

@staff_login_required
def dashboard(request):
    context = calculate_statistics()
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
def upload_photo(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  
    else:
        form = AnnouncementForm()
    return render(request, 'base/staff-section/upload_photo.html', {'form': form})
