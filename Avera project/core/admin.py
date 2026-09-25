from django.contrib import admin
from .models import (
    CareOrganization, Child, AdoptionInformation,
    Wishlist, Gift, Feedback, MilestoneUpdate,
    SuccessStory, FAQ, Notification
)


@admin.register(CareOrganization)
class CareOrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'verification_status', 'created_at')
    list_filter = ('verification_status',)
    search_fields = ('name', 'email', 'phone')


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'gender', 'adoption_status', 'care_organization', 'created_at')
    list_filter = ('adoption_status', 'gender', 'care_organization')
    search_fields = ('name', 'description')


@admin.register(AdoptionInformation)
class AdoptionInformationAdmin(admin.ModelAdmin):
    list_display = ('title', 'updated_at')
    search_fields = ('title', 'description', 'eligibility')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'organization', 'quantity_needed', 'quantity_received', 'priority', 'status')
    list_filter = ('priority', 'status', 'organization')
    search_fields = ('item_name', 'title')


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ('id', 'gift_type', 'donor', 'organization', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'gift_type', 'organization')
    search_fields = ('donor__email', 'donor__first_name', 'donor__last_name', 'description')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('gift', 'verification_status', 'feedback_date')
    list_filter = ('verification_status',)


@admin.register(MilestoneUpdate)
class MilestoneUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'child', 'update_date')
    search_fields = ('title', 'child__name')


@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'publication_date')
    search_fields = ('title', 'story_description')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category')
    list_filter = ('category',)
    search_fields = ('question', 'answer')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'is_read', 'notification_date')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__email', 'message')
