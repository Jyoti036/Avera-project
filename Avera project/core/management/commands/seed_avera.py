from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import (
    CareOrganization, Child, AdoptionInformation,
    Wishlist, Gift, Feedback, MilestoneUpdate,
    SuccessStory, FAQ, Notification
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed AVERA platform with initial test data matching presentation slides"

    def handle(self, *args, **options):
        self.stdout.write("Seeding AVERA database...")

        # 1. Create Default Admin
        admin_email = "admin@avera.org"
        admin_user, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'first_name': 'Avera',
                'last_name': 'Administrator',
                'phone': '+1 (555) 019-2831',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created Admin: {admin_email} / admin123"))
        else:
            self.stdout.write(f"Admin already exists: {admin_email}")

        # 2. Create Sample Donor User
        user_email = "donor@example.com"
        sample_user, created = User.objects.get_or_create(
            email=user_email,
            defaults={
                'first_name': 'Rahim',
                'last_name': 'Chowdhury',
                'phone': '+1 (555) 948-1122',
                'role': 'USER',
                'user_type': 'donor',
                'address': 'Dhaka, Bangladesh',
            }
        )
        if created:
            sample_user.set_password('user123')
            sample_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created Sample Donor: {user_email} / user123"))

        # 3. Create Care Organizations
        org1, _ = CareOrganization.objects.get_or_create(
            name="Hope Sunshine Children Home",
            defaults={
                'address': 'Road 12, Banani, Dhaka',
                'phone': '+880 1711-223344',
                'email': 'contact@hopesunshine.org',
                'description': 'A verified residential child shelter nurturing 45 children with education, healthcare, and loving social care.',
                'verification_status': 'Verified',
                'website': 'https://example.org/hopesunshine'
            }
        )

        org2, _ = CareOrganization.objects.get_or_create(
            name="Green Valley Foster Care",
            defaults={
                'address': 'Sector 7, Uttara, Dhaka',
                'phone': '+880 1819-556677',
                'email': 'support@greenvalleycare.org',
                'description': 'Dedicated sanctuary for orphaned and abandoned infants and toddlers, fostering family reintegration and legal adoption placement.',
                'verification_status': 'Verified',
                'website': 'https://example.org/greenvalley'
            }
        )

        # 4. Create Children Profiles
        Child.objects.get_or_create(
            name="Leo",
            care_organization=org1,
            defaults={
                'age': 6,
                'gender': 'Male',
                'description': 'Curious, cheerful boy who loves drawing and assembling building blocks. Healthy and eagerly participating in kindergarten classes.',
                'health_status': 'Completely healthy, all vaccines up to date',
                'adoption_status': 'Available'
            }
        )

        Child.objects.get_or_create(
            name="Maya",
            care_organization=org1,
            defaults={
                'age': 4,
                'gender': 'Female',
                'description': 'Friendly toddler with a bright smile. Enjoys story books, music, and group games with care teachers.',
                'health_status': 'Normal development, robust health',
                'adoption_status': 'Available'
            }
        )

        Child.objects.get_or_create(
            name="Ayaan",
            care_organization=org2,
            defaults={
                'age': 7,
                'gender': 'Male',
                'description': 'Enthusiastic student fond of mathematics, sports, and reading adventure stories.',
                'health_status': 'Healthy',
                'adoption_status': 'Supported'
            }
        )

        # 5. Adoption Information Guidelines
        AdoptionInformation.objects.get_or_create(
            title="Comprehensive Legal Adoption Framework",
            defaults={
                'description': 'Adoption is a legal and emotional commitment where a child is permanently placed with prospective parents with full filial rights.',
                'eligibility': '- Prospective adoptive parents must be physically, mentally, and financially capable.\n- Both married couples (in a stable marital relationship) and single individuals may qualify according to jurisdiction.\n- Minimum age gap between adoptive parents and the child should be at least 21 years.\n- Clear criminal record and child welfare clearance.',
                'required_documents': '1. Proof of identity (National ID / Passport)\n2. Proof of residence and financial stability (Tax returns, salary statements)\n3. Medical fitness certificate\n4. Marriage certificate (if applicable)\n5. Character reference letters from community referees',
                'adoption_process': 'Step 1: Formal Registration with Statutory Child Welfare Committee.\nStep 2: Home Study Report conducted by a certified social worker.\nStep 3: Referral & Matching of child profile based on best interest of the child.\nStep 4: Court Petition filed before the authorized Family Court.\nStep 5: Official Legal Adoption Decree issued by the judge.',
                'contact_information': 'Central Child Welfare & Family Court Helpline:\nEmail: helpline@childwelfare.gov.bd\nPhone: 1098 / +880 2 9876543\nOffice: Child Welfare Statutory Directorate'
            }
        )

        # 6. Wishlist Campaigns
        w1, _ = Wishlist.objects.get_or_create(
            organization=org1,
            item_name="Primary School Backpacks & Stationery Sets",
            defaults={
                'title': 'Back to School 2026 Drive',
                'description': 'Sturdy waterproof backpacks filled with notebooks, pencil cases, geometry sets, and coloring pencils for elementary children.',
                'quantity_needed': 30,
                'quantity_received': 12,
                'priority': 'High',
                'status': 'Partially_Fulfilled'
            }
        )

        w2, _ = Wishlist.objects.get_or_create(
            organization=org1,
            item_name="Winter Warm Blankets & Thermal Sets",
            defaults={
                'title': 'Winter Warmth for Toddlers',
                'description': 'Soft fleece blankets and warm thermal jackets to protect toddlers from seasonal respiratory ailments.',
                'quantity_needed': 25,
                'quantity_received': 20,
                'priority': 'Urgent',
                'status': 'Partially_Fulfilled'
            }
        )

        w3, _ = Wishlist.objects.get_or_create(
            organization=org2,
            item_name="Children Story & Picture Encyclopedia Books",
            defaults={
                'title': 'Little Explorers Library Corner',
                'description': 'Illustrated bilingual children books and science encyclopedias to furnish our new study room.',
                'quantity_needed': 40,
                'quantity_received': 40,
                'priority': 'Medium',
                'status': 'Fulfilled'
            }
        )

        # 7. Sample Gift and Transparency Feedback
        gift1, _ = Gift.objects.get_or_create(
            donor=sample_user,
            organization=org1,
            description="10 Sets of Class 1-4 Notebooks and Colored Pencils",
            defaults={
                'wishlist_item': w1,
                'gift_type': 'Books_Stationery',
                'quantity': 10,
                'status': 'Acknowledged',
                'tracking_reference': 'DHL-EXPRESS-992144'
            }
        )

        Feedback.objects.get_or_create(
            gift=gift1,
            defaults={
                'message': 'Received with enormous gratitude! The notebooks and pencils were distributed to Maya and classmates for their art lessons.',
                'verification_status': 'Verified'
            }
        )

        Notification.objects.get_or_create(
            user=sample_user,
            message="Your gift of 10 Educational Supplies for Hope Sunshine Children Home was verified and acknowledged with proof!",
            defaults={
                'notification_type': 'Gift_Update',
                'is_read': False
            }
        )

        # 8. Success Stories
        SuccessStory.objects.get_or_create(
            title="A New Beginning: How Kian Found His Forever Family",
            defaults={
                'story_description': 'After spending three years under dedicated care at Hope Sunshine Home, 5-year-old Kian officially joined the Ahmed family through transparent legal adoption. Today, Kian is excelling in school and surrounded by unconditional love.',
                'organization': org1,
                'publication_date': timezone.now().date()
            }
        )

        SuccessStory.objects.get_or_create(
            title="The Impact of a Single Science Kit: Anika's Dream",
            defaults={
                'story_description': 'A donor fulfilled a wishlist item for elementary science experiments. Anika, inspired by the telescope and microscope, secured first place in the regional science fair and dreams of becoming an astronomer.',
                'organization': org2,
                'publication_date': timezone.now().date()
            }
        )

        # 9. FAQs
        FAQ.objects.get_or_create(
            question="Can single individuals adopt through official channels?",
            defaults={
                'answer': 'Yes, in most jurisdictions, single individuals who meet financial, psychological, and age suitability requirements are legally eligible to adopt.',
                'category': 'Adoption'
            }
        )

        FAQ.objects.get_or_create(
            question="How do I ensure my gifts reach the children safely?",
            defaults={
                'answer': 'AVERA partners strictly with physically audited and registered care organizations. Once your gift arrives, the organization uploads a verified delivery receipt and impact proof directly visible in your dashboard.',
                'category': 'Donations'
            }
        )

        FAQ.objects.get_or_create(
            question="How is child privacy protected while displaying wishlists?",
            defaults={
                'answer': 'AVERA follows strict Child Safeguarding Protocols. Full legal names, sensitive medical history, and geolocation markers are kept confidential. Wishlists focus on items and group welfare rather than identifying details.',
                'category': 'Child_Safety'
            }
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded AVERA sample data!"))
