# homepage/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# Registration Form
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    #role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    def clean_phone_number(self): # clean number data / numeric chars only
        phone = self.cleaned_data['phone_number']
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain digits only.")
        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")

        return phone

    def clean_email(self): # clean email data / no duplicate email
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'address',
            'phone_number',
            'site',
            'password1',
            'password2',
        ]

# Login Form
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput)

# Edit Client Form
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'address',
            'phone_number',
        ]