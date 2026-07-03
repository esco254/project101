from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Staff

class StaffRegistrationForm(forms.ModelForm):
    Username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Staff
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            staff = Staff(user=user)
            staff.save()
        return user
    
    class StaffLoginForm(AuthenticationForm):
        username = forms.CharField(max_length=150)
        password = forms.CharField(widget=forms.PasswordInput)

    def save(self, commit=True):
        #superuser
        user = User(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last name']
        )
    user.set_password(self.cleaned_data['password'])
    if commit:
        staff.save()
        return staff
    
class BookingForm(forms.ModelForm):

class Meta:
    model = Booking
    fields = ['guest', 'room', 'check_in', 'check_out']
    widgets = {
        'guest' : forms.Select(attrs={'class': 'form_control'}),
        'room' : forms.Select(attrs={'class': 'form_control'}),
        'check_in' : forms.DateInput(attrs={'class': 'form_control', 'type': 'date'}),
        'check_out' : forms.DateInput(attrs={'class': 'form_control', 'type': 'date'})
    }