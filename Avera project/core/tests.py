from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import CareOrganization, Child, Wishlist, Gift, Feedback, Notification

User = get_user_model()


class CorePlatformTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='donor@test.com',
            password='Password123',
            first_name='Test',
            last_name='Donor',
            role='USER'
        )
        self.admin = User.objects.create_superuser(
            email='admin@test.com',
            password='AdminPassword123',
            first_name='Admin',
            last_name='Staff'
        )
        self.org = CareOrganization.objects.create(
            name="Loving Care Sanctuary",
            address="123 Care Street",
            phone="+12345678",
            email="care@example.com",
            description="A sanctuary for children in need."
        )
        self.wishlist = Wishlist.objects.create(
            organization=self.org,
            title="Winter Care Drive",
            item_name="Warm Blankets",
            description="Warm blankets for winter",
            quantity_needed=10,
            quantity_received=0,
            priority="Urgent"
        )

    def test_public_pages_render(self):
        """Test home, adoption info, wishlists, stories, faqs, about pages render with HTTP 200"""
        pages = ['home', 'adoption_info', 'wishlists', 'success_stories', 'faqs', 'about']
        for page in pages:
            res = self.client.get(reverse(page))
            self.assertEqual(res.status_code, 200)

    def test_pledge_gift_flow(self):
        """Test user pledging a gift increments wishlist and sends notification"""
        self.client.login(email='donor@test.com', password='Password123')
        response = self.client.post(reverse('pledge_gift_item', kwargs={'wishlist_id': self.wishlist.id}), {
            'organization': self.org.id,
            'gift_type': 'Clothes',
            'quantity': 4,
            'description': '4 Soft Warm Fleece Blankets',
            'tracking_reference': 'SHIP-12345'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user_dashboard'))

        gift = Gift.objects.filter(donor=self.user).first()
        self.assertIsNotNone(gift)
        self.assertEqual(gift.quantity, 4)

        # Check wishlist quantity received was incremented
        self.wishlist.refresh_from_db()
        self.assertEqual(self.wishlist.quantity_received, 4)
        self.assertEqual(self.wishlist.status, 'Partially_Fulfilled')

        # Check notification was created
        notif = Notification.objects.filter(user=self.user).first()
        self.assertIsNotNone(notif)

    def test_admin_dashboard_security(self):
        """Test regular user cannot access admin dashboard, only admin can"""
        # Unauthenticated user
        res = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse('admin_login'), res.url)

        # Regular user
        self.client.login(email='donor@test.com', password='Password123')
        res = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse('admin_login'), res.url)

        # Admin user
        self.client.login(email='admin@test.com', password='AdminPassword123')
        res = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(res.status_code, 200)

    def test_admin_update_gift_and_proof(self):
        """Test admin updating gift status to Acknowledged and adding proof feedback"""
        gift = Gift.objects.create(
            donor=self.user,
            organization=self.org,
            gift_type='Clothes',
            quantity=2,
            description='Warm sweaters',
            status='Pledged'
        )

        self.client.login(email='admin@test.com', password='AdminPassword123')
        res = self.client.post(reverse('admin_update_gift_status', kwargs={'gift_id': gift.id}), {
            'status': 'Acknowledged',
            'feedback_message': 'Received with thankfulness, handed over to children today!'
        })
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('admin_manage_gifts'))

        gift.refresh_from_db()
        self.assertEqual(gift.status, 'Acknowledged')
        self.assertTrue(hasattr(gift, 'proof_feedback'))
        self.assertEqual(gift.proof_feedback.message, 'Received with thankfulness, handed over to children today!')
