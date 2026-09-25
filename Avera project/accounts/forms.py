from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from django.core.exceptions import ValidationError

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter strong password (min 6 characters)',
            'id': 'user_reg_password'
        }),
        label="Password",
        min_length=6
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'id': 'user_reg_password_confirm'
        }),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'user_type']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 234 567 8900'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, Country (Optional)'}),
            'user_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match. Please re-enter.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'USER'
        user.is_staff = False
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com',
            'autocomplete': 'email',
            'autofocus': True
        }),
        label="Email Address"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        }),
        label="Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email.strip().lower(), password=password)
            if user is None:
                raise ValidationError("Invalid email or password. Please check your credentials.")
            if not user.is_active:
                raise ValidationError("This account has been deactivated. Please contact support.")
            cleaned_data['user'] = user
        return cleaned_data


class AdminRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter administrator password (min 6 characters)',
        }),
        label="Password",
        min_length=6
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm administrator password',
        }),
        label="Confirm Password"
    )
    admin_secret_key = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Admin Access Passcode',
        }),
        label="Admin Authorization Passcode",
        help_text="Required security code for creating administrator accounts."
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Admin First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Admin Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'admin@avera.org'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 234 567 8900'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean_admin_secret_key(self):
        key = self.cleaned_data.get('admin_secret_key')
        expected_key = getattr(settings, 'ADMIN_SECRET_KEY', 'AVERA_ADMIN_2026')
        if key != expected_key:
            raise ValidationError("Invalid Admin Authorization Passcode. Administrator creation unauthorized.")
        return key

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'ADMIN'
        user.is_staff = True
        if commit:
            user.save()
        return user


class AdminLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'admin@avera.org',
            'autocomplete': 'email',
            'autofocus': True
        }),
        label="Admin Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter admin password',
            'autocomplete': 'current-password'
        }),
        label="Admin Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email.strip().lower(), password=password)
            if user is None:
                raise ValidationError("Invalid administrator credentials.")
            if not user.is_active:
                raise ValidationError("This administrator account has been deactivated.")
            if not (user.role == 'ADMIN' or user.is_staff or user.is_superuser):
                raise ValidationError("Access restricted: This account does not possess administrator privileges.")
            cleaned_data['user'] = user
        return cleaned_data


class PasswordResetEmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email address',
            'autocomplete': 'email',
            'autofocus': True
        }),
        label="Account Email"
    )

    def __init__(self, *args, **kwargs):
        self.role_scope = kwargs.pop('role_scope', None)  # 'USER' or 'ADMIN'
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        query = User.objects.filter(email__iexact=email, is_active=True)
        if self.role_scope == 'ADMIN':
            query = query.filter(role='ADMIN')
        elif self.role_scope == 'USER':
            query = query.filter(role='USER')

        if not query.exists():
            raise ValidationError(f"No active {'administrator' if self.role_scope == 'ADMIN' else 'user'} account found with this email.")
        return email


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password (min 6 characters)'
        }),
        label="New Password",
        min_length=6
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        }),
        label="Confirm New Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data
