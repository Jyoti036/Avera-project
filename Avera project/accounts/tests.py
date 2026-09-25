from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core import mail

User = get_user_model()


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_registration(self):
        """User registration with first name, last name, email, phone, and password"""
        response = self.client.post(reverse('user_register'), {
            'first_name': 'Sarah',
            'last_name': 'Ali',
            'email': 'sarah@example.com',
            'phone': '+1234567890',
            'password': 'StrongPassword123',
            'password_confirm': 'StrongPassword123',
            'user_type': 'donor'
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(email='sarah@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'Sarah')
        self.assertEqual(user.last_name, 'Ali')
        self.assertEqual(user.phone, '+1234567890')
        self.assertEqual(user.role, 'USER')
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password('StrongPassword123'))

    def test_user_login(self):
        """User login using email and password"""
        User.objects.create_user(
            email='testuser@example.com',
            password='TestPassword123',
            first_name='John',
            last_name='Doe',
            role='USER'
        )
        response = self.client.post(reverse('user_login'), {
            'email': 'testuser@example.com',
            'password': 'TestPassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user_dashboard'))

    def test_user_password_reset_email_verification(self):
        """User password reset sends verification email with token link, then resets password"""
        user = User.objects.create_user(
            email='forgetful@example.com',
            password='OldPassword123',
            first_name='Forgetful',
            last_name='User',
            role='USER'
        )
        
        # Step 1: Request reset
        response = self.client.post(reverse('user_password_reset'), {
            'email': 'forgetful@example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Reset Your Password", mail.outbox[0].subject)

        # Step 2: Use token from email link to confirm reset
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        confirm_url = reverse('user_password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        get_res = self.client.get(confirm_url)
        self.assertEqual(get_res.status_code, 200)

        # Step 3: Set new password
        post_res = self.client.post(confirm_url, {
            'new_password': 'BrandNewPassword123',
            'confirm_password': 'BrandNewPassword123'
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertRedirects(post_res, reverse('user_login'))

        # Step 4: Verify new password allows login
        login_res = self.client.post(reverse('user_login'), {
            'email': 'forgetful@example.com',
            'password': 'BrandNewPassword123'
        })
        self.assertEqual(login_res.status_code, 302)
        self.assertRedirects(login_res, reverse('user_dashboard'))

    def test_admin_registration(self):
        """Admin registration through dedicated hidden portal with security passcode"""
        response = self.client.post(reverse('admin_register'), {
            'first_name': 'Chief',
            'last_name': 'Officer',
            'email': 'chief@avera.org',
            'phone': '+1987654321',
            'password': 'AdminSecurePassword123',
            'password_confirm': 'AdminSecurePassword123',
            'admin_secret_key': 'AVERA_ADMIN_2026'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_login'))
        admin = User.objects.filter(email='chief@avera.org').first()
        self.assertIsNotNone(admin)
        self.assertEqual(admin.role, 'ADMIN')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.check_password('AdminSecurePassword123'))

    def test_admin_login(self):
        """Admin login authenticates and directs to admin dashboard"""
        User.objects.create_superuser(
            email='portaladmin@avera.org',
            password='AdminPassword123',
            first_name='Portal',
            last_name='Admin'
        )
        response = self.client.post(reverse('admin_login'), {
            'email': 'portaladmin@avera.org',
            'password': 'AdminPassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_admin_password_reset_email_verification(self):
        """Admin password reset flow with email verification"""
        admin = User.objects.create_superuser(
            email='adminreset@avera.org',
            password='OldAdminPass123',
            first_name='Reset',
            last_name='Admin'
        )

        response = self.client.post(reverse('admin_password_reset'), {
            'email': 'adminreset@avera.org'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

        uid = urlsafe_base64_encode(force_bytes(admin.pk))
        token = default_token_generator.make_token(admin)
        confirm_url = reverse('admin_password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        res = self.client.post(confirm_url, {
            'new_password': 'UpdatedAdminPass123',
            'confirm_password': 'UpdatedAdminPass123'
        })
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('admin_login'))

    def test_public_navbar_does_not_show_admin_login_or_register(self):
        """Ensure admin login/registration links are NOT shown in the public navbar or pages"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        
        # User login and register SHOULD be visible
        self.assertIn(reverse('user_login'), content)
        self.assertIn(reverse('user_register'), content)

        # Admin login and register links should NOT be shown in public navbar
        self.assertNotIn(reverse('admin_login'), content)
        self.assertNotIn(reverse('admin_register'), content)
