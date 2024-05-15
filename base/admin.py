from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import User, Adult, Pediatric, Child

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    birth_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'middle_name', 'last_name', 'email_address', 'phone_number', 'birth_date', 'position', 'is_staff', 'is_superuser')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'middle_name', 'last_name', 'email_address', 'phone_number', 'birth_date', 'position', 'is_staff', 'is_superuser')

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'middle_name', 'last_name', 'email_address', 'phone_number', 'birth_date', 'position')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'middle_name', 'last_name', 'email_address', 'phone_number', 'birth_date', 'position', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['birth_date'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        return form

admin.site.register(User, CustomUserAdmin)
admin.site.register(Adult)
admin.site.register(Pediatric)
admin.site.register(Child)
