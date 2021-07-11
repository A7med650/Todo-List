from django.shortcuts import render, redirect
from django.contrib import messages
from validate_email import validate_email
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from .models import User
from .decorators import auth_user_should_not_access

# Create your views here.


@auth_user_should_not_access
def register(request):
    if request.method == 'POST':
        context = {
            'has_error': False,
            'data': request.POST,
        }
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if len(password1) < 6:
            messages.add_message(request, messages.ERROR,
                                 "Password should be at least 6 characters")
            context['has_error'] = True

        if password1 != password2:
            messages.add_message(request, messages.ERROR, "Password mismatch")
            context['has_error'] = True

        if not validate_email(email):
            messages.add_message(request, messages.ERROR,
                                 "Enter a valid email address")
            context['has_error'] = True

        if not username:
            messages.add_message(request, messages.ERROR,
                                 "Username is required")
            context['has_error'] = True

        if User.objects.filter(username=username).exists():
            messages.add_message(request, messages.ERROR,
                                 "Username is taken, choose another one")
            context['has_error'] = True

        if User.objects.filter(email=email).exists():
            messages.add_message(request, messages.ERROR,
                                 "Email is taken, choose another one")
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'register.html', context)

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password1)
        user.save()

        messages.add_message(request, messages.SUCCESS,
                             "Account created, you can now login")

        return redirect('authentication:login')

    return render(request, 'register.html')


@auth_user_should_not_access
def login_user(request):

    if request.method == "POST":
        context = {
            'data': request.POST,
        }
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if not user:
            messages.add_message(request, messages.ERROR,
                                 "invalid credentials")
            return render(request, 'login.html', context)

        login(request, user)
        messages.add_message(request, messages.SUCCESS,
                             f"Welcome {user.username}")
        return redirect(reverse('todo:index'))

    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, "Successfully logged out")
    return redirect(reverse('authentication:login'))
