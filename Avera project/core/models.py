from django.db import models
from django.conf import settings
from django.utils import timezone


class CareOrganization(models.Model):
    VERIFICATION_STATUS = (
        ('Pending', 'Pending Verification'),
        ('Verified', 'Verified Organization'),
        ('Rejected', 'Rejected'),
    )

    name = models.CharField(max_length=200, verbose_name="Organization Name")
    address = models.TextField(verbose_name="Address")
    phone = models.CharField(max_length=30, verbose_name="Phone")
    email = models.EmailField(verbose_name="Email")
    description = models.TextField(verbose_name="Description")
    verification_status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS, 
        default='Verified',
        verbose_name="Verification Status"
    )
    website = models.URLField(blank=True, null=True, verbose_name="Website")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Care Organization"
        verbose_name_plural = "Care Organizations"


class Child(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    ADOPTION_STATUS = (
        ('Available', 'Available for Adoption Inquiries'),
        ('In_Process', 'In Process'),
        ('Supported', 'Supported by Donor Gifts'),
        ('Adopted', 'Adopted'),
    )

    name = models.CharField(max_length=100, verbose_name="Child Alias / Name")
    age = models.PositiveIntegerField(verbose_name="Age")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    description = models.TextField(verbose_name="Background / About Child")
    health_status = models.CharField(max_length=150, default="Healthy", verbose_name="Health Status")
    adoption_status = models.CharField(
        max_length=20, 
        choices=ADOPTION_STATUS, 
        default='Available',
        verbose_name="Status"
    )
    care_organization = models.ForeignKey(
        CareOrganization, 
        on_delete=models.CASCADE, 
        related_name="children",
        verbose_name="Care Organization"
    )
    photo = models.ImageField(upload_to="children/", blank=True, null=True, verbose_name="Photo")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.age} yrs) - {self.care_organization.name}"

    class Meta:
        verbose_name = "Child Profile"
        verbose_name_plural = "Child Profiles"


class AdoptionInformation(models.Model):
    title = models.CharField(max_length=200, verbose_name="Title")
    description = models.TextField(verbose_name="Overview")
    eligibility = models.TextField(verbose_name="Eligibility Criteria")
    required_documents = models.TextField(verbose_name="Required Documents")
    adoption_process = models.TextField(verbose_name="Step-by-Step Process")
    contact_information = models.TextField(verbose_name="Official Contact Information")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Adoption Information"
        verbose_name_plural = "Adoption Information Hub"


class Wishlist(models.Model):
    PRIORITY_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High Priority'),
        ('Urgent', 'Urgent Need'),
    )

    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('Partially_Fulfilled', 'Partially Fulfilled'),
        ('Fulfilled', 'Fully Fulfilled'),
    )

    organization = models.ForeignKey(
        CareOrganization, 
        on_delete=models.CASCADE, 
        related_name="wishlists",
        verbose_name="Care Organization"
    )
    title = models.CharField(max_length=200, verbose_name="Campaign / Wish Title")
    item_name = models.CharField(max_length=150, verbose_name="Item Name")
    description = models.TextField(verbose_name="Description & Purpose")
    quantity_needed = models.PositiveIntegerField(default=1, verbose_name="Quantity Needed")
    quantity_received = models.PositiveIntegerField(default=0, verbose_name="Quantity Received")
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def remaining_needed(self):
        return max(0, self.quantity_needed - self.quantity_received)

    @property
    def progress_percentage(self):
        if self.quantity_needed == 0:
            return 100
        return min(100, int((self.quantity_received / self.quantity_needed) * 100))

    def __str__(self):
        return f"{self.item_name} ({self.organization.name}) - {self.status}"

    class Meta:
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"


class Gift(models.Model):
    GIFT_TYPE_CHOICES = (
        ('Books_Stationery', 'Educational & Books'),
        ('Clothes', 'Clothing & Footwear'),
        ('Toys_Games', 'Toys & Recreation'),
        ('Health_Nutrition', 'Nutrition & Health Supplies'),
        ('Other', 'Other Support'),
    )

    STATUS_CHOICES = (
        ('Pledged', 'Pledged by Donor'),
        ('Dispatched', 'Dispatched / In Transit'),
        ('Received', 'Received by Organization'),
        ('Acknowledged', 'Verified & Acknowledged with Proof'),
    )

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="gifts",
        verbose_name="Donor"
    )
    organization = models.ForeignKey(
        CareOrganization, 
        on_delete=models.CASCADE, 
        related_name="received_gifts",
        verbose_name="Care Organization"
    )
    wishlist_item = models.ForeignKey(
        Wishlist, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="pledges",
        verbose_name="Matched Wishlist Item"
    )
    gift_type = models.CharField(max_length=30, choices=GIFT_TYPE_CHOICES)
    description = models.TextField(verbose_name="Gift Description")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pledged')
    tracking_reference = models.CharField(max_length=100, blank=True, verbose_name="Courier / Tracking Ref")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gift #{self.id}: {self.get_gift_type_display()} by {self.donor.get_full_name()}"

    class Meta:
        verbose_name = "Gift / Support"
        verbose_name_plural = "Gifts / Supports"


class Feedback(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending Admin Verification'),
        ('Verified', 'Verified & Public Proof'),
    )

    gift = models.OneToOneField(Gift, on_delete=models.CASCADE, related_name="proof_feedback")
    message = models.TextField(verbose_name="Impact Message / Proof Note")
    photo = models.ImageField(upload_to="proofs/", blank=True, null=True, verbose_name="Proof Photo")
    feedback_date = models.DateTimeField(default=timezone.now)
    verification_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Verified')

    def __str__(self):
        return f"Feedback for Gift #{self.gift.id} ({self.verification_status})"

    class Meta:
        verbose_name = "Transparency Feedback"
        verbose_name_plural = "Transparency Feedbacks"


class MilestoneUpdate(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=200, verbose_name="Milestone Title")
    description = models.TextField(verbose_name="Progress & Growth Update")
    update_date = models.DateField(default=timezone.now)
    photo = models.ImageField(upload_to="milestones/", blank=True, null=True, verbose_name="Update Photo")

    def __str__(self):
        return f"{self.title} - {self.child.name}"

    class Meta:
        verbose_name = "Milestone & Growth Update"
        verbose_name_plural = "Milestone Updates"


class SuccessStory(models.Model):
    title = models.CharField(max_length=200, verbose_name="Story Title")
    story_description = models.TextField(verbose_name="Success Story Details")
    image = models.ImageField(upload_to="stories/", blank=True, null=True, verbose_name="Story Image")
    publication_date = models.DateField(default=timezone.now)
    organization = models.ForeignKey(
        CareOrganization, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="stories"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Success Story"
        verbose_name_plural = "Success Stories"


class FAQ(models.Model):
    CATEGORY_CHOICES = (
        ('Adoption', 'Adoption Process'),
        ('Donations', 'Donations & Gifts'),
        ('Child_Safety', 'Privacy & Child Safety'),
        ('General', 'General Questions'),
    )

    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='General')

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"


class Notification(models.Model):
    TYPE_CHOICES = (
        ('Gift_Update', 'Gift Tracking Update'),
        ('Milestone', 'Milestone & Growth Update'),
        ('Anniversary', 'Anniversary Reminder'),
        ('System', 'System Notification'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=25, choices=TYPE_CHOICES, default='System')
    message = models.TextField()
    notification_date = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.email} - {self.notification_type}"

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-notification_date']
