from django.urls import path
from . import views 
from django.conf.urls.static import static
from django.conf import settings
from .views import *


urlpatterns = [
    path('', views.home, name="home"),
    path('logout/', views.logout_client, name="logout"),
    path('login/', views.login_page, name="login"),
    path('register/', views.register_page, name="register"),

    path('staffdashboard/', views.staff_dashboard, name="staff_dashboard"),
    path('userdashboard/', views.user_dashboard, name="user_dashboard"),

    path('dashboard/', views.dashboard, name="dashboard"),
    path('staffprofile/', views.staff_profile, name="staff_profile"),
    path('unverifiedforms/', views.unverifiedforms, name="unverifiedforms"),
    path('viewrecords/', views.view_records, name="view_records"),
    path('manageusers/', views.manage_users, name="manage_users"),
    path('uploadphoto/', views.upload_photo, name="upload_photo"),
    
    path('patientprofile/', views.patient_profile, name="patient_profile"),
    path('patientrecord/', views.patient_record, name="patient_record"),
    path('data_privacy/', views.data_privacy, name='data_privacy'),

    path('choose_form/', views.choose_form_view, name='choose_form'),
    path('adultform/', views.adult_form, name="adult_form"),
    path('childform/', views.child_form, name="child_form"),
    path('pediatricform/', views.pediatric_form, name="pediatric_form"),

    path('viewform/<int:form_id>/', views.patient_view_form, name='patient_view_form'),
    path('updateform/<int:form_id>/', views.patient_update_form, name='patient_update_form'),
    path('deleteform/<int:form_id>/', views.patient_delete_form, name='patient_delete_form'),
    path('generate_pdf/<int:form_id>/', views.generate_pdf, name='generate_pdf'),

    path('staffviewform/<int:form_id>/', views.staff_view_form, name='staff_view_form'),
    path('staffupdateform/<int:form_id>/', views.staff_update_form, name='staff_update_form'),
    path('staffdeleteform/<int:form_id>/', views.staff_delete_form, name='staff_delete_form'),
    path('staffacceptform/<int:form_id>/', views.staff_accept_form, name='staff_accept_form'),
    path('staffviewprofile/<int:user_id>/', views.staff_view_profile, name='staff_view_profile'),
    path('staffsuspendprofile/<int:user_id>/', views.staff_suspend_user, name='staff_suspend_user'),
    path('staffgenerate_pdf/<int:form_id>/', views.staff_generate_pdf, name='staff_generate_pdf'),

    path('add_doctor_order/<int:form_id>/', views.add_doctor_order, name='add_doctor_order'),
    path('add_nurse_notes/<int:form_id>/', views.add_nurse_notes, name='add_nurse_notes'),

    path('searchrecords/', views.search_records, name='search_records'),
    path('searchusers/', views.search_users, name='search_users'),

    path('socialhistorydashboard/', views.social_history_analysis, name='social_history_analysis'),
    path('medicalhistorydashboard/', views.medical_history_analysis, name='medical_history_analysis'),

    path('resetpassword/', views.reset_password, name='reset_password'),
    path('password_requests/', views.password_requests, name='password_requests'),
    path('approve_password_change/<int:request_id>/', views.approve_password_change, name='approve_password_change'),
    path('reject_password_change/<int:request_id>/', views.reject_password_change, name='reject_password_change'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)