from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import (
    force_bytes,
    force_text,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from validate_email import validate_email

from .decorators import auth_user_should_not_access
from .models import User
from .utils import generate_token

# Create your views here.


def send_activation_email(user, request):
    current_site = get_current_site(request)
    email_subject = "Activate your account"
    email_body = render_to_string(
        "activate.html",
        context={
            "user": user,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": generate_token.make_token(user),
        },
    )

    email = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )
    email.send()


@auth_user_should_not_access
def register(request):
    if request.method == "POST":
        context = {
            "has_error": False,
            "data": request.POST,
        }
        email = request.POST.get("email")
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if len(password1) < 6:
            messages.add_message(
                request,
                messages.ERROR,
                "Password should be at least 6 characters",
            )
            context["has_error"] = True

        if password1 != password2:
            messages.add_message(request, messages.ERROR, "Password mismatch")
            context["has_error"] = True

        if not validate_email(email):
            messages.add_message(
                request, messages.ERROR, "Enter a valid email address"
            )
            context["has_error"] = True

        if not username:
            messages.add_message(
                request, messages.ERROR, "Username is required"
            )
            context["has_error"] = True

        if User.objects.filter(username=username).exists():
            messages.add_message(
                request,
                messages.ERROR,
                "Username is taken, choose another one",
            )
            context["has_error"] = True

        if User.objects.filter(email=email).exists():
            messages.add_message(
                request, messages.ERROR, "Email is taken, choose another one"
            )
            context["has_error"] = True

        if context["has_error"]:
            return render(request, "register.html", context)

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password1)
        user.save()

        send_activation_email(user, request)

        messages.add_message(
            request,
            messages.SUCCESS,
            "We sent you an email to verify your account",
        )

        return redirect("authentication:login")

    return render(request, "register.html")


@auth_user_should_not_access
def login_user(request):

    if request.method == "POST":
        context = {
            "data": request.POST,
        }
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if not user.is_email_verified:
            messages.add_message(
                request,
                messages.ERROR,
                "Email is not verified, please check your email inbox",
            )
            return render(request, "login.html", context)

        if not user:
            messages.add_message(
                request, messages.ERROR, "invalid credentials"
            )
            return render(request, "login.html", context)

        login(request, user)
        messages.add_message(
            request, messages.SUCCESS, f"Welcome {user.username}"
        )
        return redirect(reverse("todo:index"))

    return render(request, "login.html")


def logout_user(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, "Successfully logged out")
    return redirect(reverse("authentication:login"))


def activate_user(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()
        messages.add_message(
            request, messages.SUCCESS, "Email verified, you can now login"
        )
        return redirect(reverse("authentication:login"))

    return render(request, "activate_failed.html", {"user": user})
