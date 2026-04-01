from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegisterForm, UserLoginForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.decorators import login_required

from .utils import *

# Home page
def home(request):
    return render(request, 'homepage/home.html')

# employee dashboard
def emp(request):
    return render(request, 'emp_page/employees/dashboard.html')

# Register view
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'client' #role select
            user.save() #save to database 
                   
            #send email to client - account success
            client_accsuccess(form.cleaned_data['username'], form.cleaned_data['password1'], form.cleaned_data['email'], form.cleaned_data['site'])
            #send internal email - account success
            internal_accsuccess(form.cleaned_data['username'],form.cleaned_data['email'],form.cleaned_data['phone_number'], form.cleaned_data['site'])

            login(request, user)#auto login after creating an account
            messages.success(request, "Registration successful!")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Check the errors below.")
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.role == 'employee':
                return redirect('employee_dashboard')
            else:
                return redirect('home')

        else:
            messages.error(request, "Invalid username or password")
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('home')


#Client Edit View
User = get_user_model()

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

@login_required
def edit_account(request):
    user = request.user

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Account updated successfully.")
            return redirect('home')
    else:
        form = UserEditForm(instance=user)

    return render(request, 'accounts/edit_account.html', {'form': form})