from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import (
    CareOrganization, Child, AdoptionInformation,
    Wishlist, Gift, Feedback, MilestoneUpdate,
    SuccessStory, FAQ, Notification
)
from accounts.models import User


def is_admin_check(user):
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_staff or user.is_superuser)


# ==========================================
# PUBLIC VIEWS
# ==========================================

def home(request):
    featured_orgs = CareOrganization.objects.filter(verification_status='Verified')[:4]
    active_wishlists = Wishlist.objects.exclude(status='Fulfilled')[:6]
    stories = SuccessStory.objects.all().order_by('-publication_date')[:3]
    faqs = FAQ.objects.all()[:4]
    children_sample = Child.objects.all()[:4]

    context = {
        'featured_orgs': featured_orgs,
        'active_wishlists': active_wishlists,
        'stories': stories,
        'faqs': faqs,
        'children_sample': children_sample,
    }
    return render(request, 'core/home.html', context)


def adoption_info(request):
    info_list = AdoptionInformation.objects.all().order_by('-updated_at')
    faqs = FAQ.objects.filter(category='Adoption')
    return render(request, 'core/adoption_info.html', {
        'info_list': info_list,
        'faqs': faqs
    })


def wishlist_catalog(request):
    wishlists = Wishlist.objects.all().order_by('-created_at')
    orgs = CareOrganization.objects.all()
    selected_org = request.GET.get('org')
    if selected_org:
        wishlists = wishlists.filter(organization_id=selected_org)

    return render(request, 'core/wishlists.html', {
        'wishlists': wishlists,
        'orgs': orgs,
        'selected_org': selected_org,
    })


def success_stories(request):
    stories = SuccessStory.objects.all().order_by('-publication_date')
    return render(request, 'core/stories.html', {'stories': stories})


def faqs_view(request):
    faqs = FAQ.objects.all()
    return render(request, 'core/faqs.html', {'faqs': faqs})


def about_avera(request):
    return render(request, 'core/about.html')


# ==========================================
# USER DASHBOARD & ACTIONS (USER PROTECTED)
# ==========================================

@login_required
def user_dashboard(request):
    if request.user.role == 'ADMIN' or request.user.is_staff:
        return redirect('admin_dashboard')

    user_gifts = Gift.objects.filter(donor=request.user).order_by('-created_at')
    notifications = Notification.objects.filter(user=request.user).order_by('-notification_date')
    unread_notifications_count = notifications.filter(is_read=False).count()

    context = {
        'user_gifts': user_gifts,
        'notifications': notifications,
        'unread_count': unread_notifications_count,
        'total_gifts_pledged': user_gifts.count(),
        'fulfilled_gifts_count': user_gifts.filter(status='Acknowledged').count(),
    }
    return render(request, 'core/user_dashboard.html', context)


@login_required
def pledge_gift(request, wishlist_id=None):
    wishlist_item = None
    if wishlist_id:
        wishlist_item = get_object_or_404(Wishlist, id=wishlist_id)

    orgs = CareOrganization.objects.filter(verification_status='Verified')

    if request.method == 'POST':
        org_id = request.POST.get('organization')
        gift_type = request.POST.get('gift_type')
        description = request.POST.get('description')
        quantity = int(request.POST.get('quantity', 1))
        tracking_reference = request.POST.get('tracking_reference', '')

        org = get_object_or_404(CareOrganization, id=org_id)

        gift = Gift.objects.create(
            donor=request.user,
            organization=org,
            wishlist_item=wishlist_item,
            gift_type=gift_type,
            description=description,
            quantity=quantity,
            tracking_reference=tracking_reference,
            status='Pledged'
        )

        # Update wishlist if matched
        if wishlist_item:
            wishlist_item.quantity_received += quantity
            if wishlist_item.quantity_received >= wishlist_item.quantity_needed:
                wishlist_item.status = 'Fulfilled'
            else:
                wishlist_item.status = 'Partially_Fulfilled'
            wishlist_item.save()

        # Send notification to donor
        Notification.objects.create(
            user=request.user,
            notification_type='Gift_Update',
            message=f"Thank you for pledging {quantity} {gift.get_gift_type_display()} for {org.name}!"
        )

        messages.success(request, f"Your gift pledge for {org.name} has been recorded! Thank you for supporting our children.")
        return redirect('user_dashboard')

    return render(request, 'core/pledge_gift.html', {
        'wishlist_item': wishlist_item,
        'orgs': orgs
    })


@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect('user_dashboard')


# ==========================================
# ADMIN DASHBOARD & MANAGEMENT (ADMIN ONLY)
# ==========================================

@user_passes_test(is_admin_check, login_url='admin_login')
def admin_dashboard(request):
    total_users = User.objects.filter(role='USER').count()
    total_orgs = CareOrganization.objects.count()
    total_children = Child.objects.count()
    total_wishlists = Wishlist.objects.count()
    total_gifts = Gift.objects.count()
    pending_gifts = Gift.objects.filter(status='Pledged').count()

    recent_gifts = Gift.objects.all().order_by('-created_at')[:8]
    recent_users = User.objects.filter(role='USER').order_by('-date_joined')[:6]

    context = {
        'total_users': total_users,
        'total_orgs': total_orgs,
        'total_children': total_children,
        'total_wishlists': total_wishlists,
        'total_gifts': total_gifts,
        'pending_gifts': pending_gifts,
        'recent_gifts': recent_gifts,
        'recent_users': recent_users,
    }
    return render(request, 'core/admin_dashboard.html', context)


@user_passes_test(is_admin_check, login_url='admin_login')
def admin_manage_gifts(request):
    gifts = Gift.objects.all().order_by('-created_at')
    return render(request, 'core/admin_manage_gifts.html', {'gifts': gifts})


@user_passes_test(is_admin_check, login_url='admin_login')
def admin_update_gift_status(request, gift_id):
    gift = get_object_or_404(Gift, id=gift_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        feedback_message = request.POST.get('feedback_message', '').strip()

        gift.status = new_status
        gift.save()

        # If acknowledged or proof provided
        if feedback_message:
            Feedback.objects.update_or_create(
                gift=gift,
                defaults={
                    'message': feedback_message,
                    'verification_status': 'Verified',
                    'feedback_date': timezone.now()
                }
            )

        # Notify donor
        Notification.objects.create(
            user=gift.donor,
            notification_type='Gift_Update',
            message=f"Update on your Gift #{gift.id} ({gift.get_gift_type_display()}): Status changed to '{gift.get_status_display()}'."
        )

        messages.success(request, f"Gift #{gift.id} status updated to {new_status}.")
        return redirect('admin_manage_gifts')

    return render(request, 'core/admin_update_gift.html', {'gift': gift})


@user_passes_test(is_admin_check, login_url='admin_login')
def admin_manage_children(request):
    children = Child.objects.all().order_by('-created_at')
    orgs = CareOrganization.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        description = request.POST.get('description')
        health_status = request.POST.get('health_status', 'Healthy')
        adoption_status = request.POST.get('adoption_status', 'Available')
        org_id = request.POST.get('care_organization')

        org = get_object_or_404(CareOrganization, id=org_id)
        Child.objects.create(
            name=name,
            age=age,
            gender=gender,
            description=description,
            health_status=health_status,
            adoption_status=adoption_status,
            care_organization=org
        )
        messages.success(request, f"Child profile '{name}' successfully added.")
        return redirect('admin_manage_children')

    return render(request, 'core/admin_manage_children.html', {
        'children': children,
        'orgs': orgs
    })


@user_passes_test(is_admin_check, login_url='admin_login')
def admin_manage_wishlists(request):
    wishlists = Wishlist.objects.all().order_by('-created_at')
    orgs = CareOrganization.objects.all()

    if request.method == 'POST':
        org_id = request.POST.get('organization')
        title = request.POST.get('title')
        item_name = request.POST.get('item_name')
        description = request.POST.get('description')
        quantity_needed = int(request.POST.get('quantity_needed', 1))
        priority = request.POST.get('priority', 'Medium')

        org = get_object_or_404(CareOrganization, id=org_id)
        Wishlist.objects.create(
            organization=org,
            title=title,
            item_name=item_name,
            description=description,
            quantity_needed=quantity_needed,
            priority=priority,
            status='Open'
        )
        messages.success(request, f"New wishlist item '{item_name}' added for {org.name}.")
        return redirect('admin_manage_wishlists')

    return render(request, 'core/admin_manage_wishlists.html', {
        'wishlists': wishlists,
        'orgs': orgs
    })
