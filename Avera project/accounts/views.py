import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    AdminRegistrationForm,
    AdminLoginForm,
    PasswordResetEmailForm,
    SetNewPasswordForm,
)

User = get_user_model()
logger = logging.getLogger(__name__)


# ==========================================
# USER AUTHENTICATION VIEWS
# ==========================================

def user_register(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Welcome to AVERA, {user.first_name}! Your account has been created successfully. You can now log in.")
            return redirect('user_login')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/user_register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'ADMIN' or request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('user_dashboard')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/user_login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


def user_password_reset(request):
    if request.method == 'POST':
        form = PasswordResetEmailForm(request.POST, role_scope='USER')
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email__iexact=email, role='USER')
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            reset_url = request.build_absolute_uri(
                reverse('user_password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            subject = "AVERA - Reset Your Password"
            message = (
                f"Hello {user.get_full_name()},\n\n"
                f"You requested a password reset for your AVERA account.\n"
                f"Please click the verification link below to set a new password:\n\n"
                f"{reset_url}\n\n"
                f"If you did not request this, please ignore this email. Your password will remain unchanged.\n\n"
                f"Warm regards,\n"
                f"AVERA Child Adoption & Support Team"
            )
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False
                )
            except Exception as e:
                logger.error(f"Error sending email: {e}")

            # Keep the reset url in request session for dev preview ease
            request.session['dev_last_user_reset_url'] = reset_url
            return redirect('user_password_reset_done')
    else:
        form = PasswordResetEmailForm(role_scope='USER')

    return render(request, 'accounts/user_password_reset.html', {'form': form})


def user_password_reset_done(request):
    dev_reset_url = request.session.get('dev_last_user_reset_url')
    return render(request, 'accounts/user_password_reset_done.html', {
        'dev_reset_url': dev_reset_url,
        'is_admin': False
    })


def user_password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid, role='USER')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(request, 'accounts/password_reset_invalid.html', {'is_admin': False})

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, "Your password has been successfully reset! You can now log in.")
            return redirect('user_login')
    else:
        form = SetNewPasswordForm()

    return render(request, 'accounts/user_password_reset_confirm.html', {'form': form, 'user_target': user})


# ==========================================
# ADMIN AUTHENTICATION VIEWS (HIDDEN PORTAL)
# ==========================================

def admin_register(request):
    if request.user.is_authenticated and (request.user.role == 'ADMIN' or request.user.is_staff):
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            admin_user = form.save()
            messages.success(
                request, 
                f"Administrator account for {admin_user.get_full_name()} successfully created. Please sign in."
            )
            return redirect('admin_login')
    else:
        form = AdminRegistrationForm()

    return render(request, 'accounts/admin_register.html', {
        'form': form,
        'passcode_hint': getattr(settings, 'ADMIN_SECRET_KEY', 'AVERA_ADMIN_2026')
    })


def admin_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'ADMIN' or request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            messages.warning(request, "You are logged in as a regular user. Admin credentials required.")

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, f"Welcome to AVERA Admin Portal, {user.first_name}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('admin_dashboard')
    else:
        form = AdminLoginForm()

    return render(request, 'accounts/admin_login.html', {'form': form})


def admin_logout(request):
    logout(request)
    messages.info(request, "Administrator has been logged out.")
    return redirect('admin_login')


def admin_password_reset(request):
    if request.method == 'POST':
        form = PasswordResetEmailForm(request.POST, role_scope='ADMIN')
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email__iexact=email, role='ADMIN')
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            reset_url = request.build_absolute_uri(
                reverse('admin_password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            subject = "AVERA Admin Portal - Password Reset Verification"
            message = (
                f"Hello Admin {user.get_full_name()},\n\n"
                f"A password reset request was initiated for your administrator account.\n"
                f"Verify your email and reset your administrator password via this secure link:\n\n"
                f"{reset_url}\n\n"
                f"Security notice: If you did not make this request, verify your account security immediately.\n\n"
                f"AVERA System Security"
            )
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False
                )
            except Exception as e:
                logger.error(f"Error sending admin email: {e}")

            request.session['dev_last_admin_reset_url'] = reset_url
            return redirect('admin_password_reset_done')
    else:
        form = PasswordResetEmailForm(role_scope='ADMIN')

    return render(request, 'accounts/admin_password_reset.html', {'form': form})


def admin_password_reset_done(request):
    dev_reset_url = request.session.get('dev_last_admin_reset_url')
    return render(request, 'accounts/admin_password_reset_done.html', {
        'dev_reset_url': dev_reset_url,
        'is_admin': True
    })


def admin_password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid, role='ADMIN')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(request, 'accounts/password_reset_invalid.html', {'is_admin': True})

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, "Administrator password successfully reset! You can now log in.")
            return redirect('admin_login')
    else:
        form = SetNewPasswordForm()

    return render(request, 'accounts/admin_password_reset_confirm.html', {'form': form, 'user_target': user})
