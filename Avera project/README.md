# AVERA — Child Adoption Awareness & Support Platform

> *"Every adoption starts with inspiration, ends with a gift, and lives on through the stories that prove it."*  
> **Academic CEP Project by Group 4**

---

## 🌟 Project Overview

**AVERA** is a web-based platform built on Django designed to promote child adoption awareness, guide prospective parents with reliable legal and procedural information, and connect supporters with verified care organizations through transparent gift contributions.

### ✨ Key Features Implemented:
1. **Adoption Information Hub**: Official criteria, required documentation, and step-by-step guidance.
2. **Wishlist Matching System**: Care organizations post specific needed items (books, clothing, health supplies); donors pledge and fulfill them directly.
3. **Transparency & Proof of Impact**: Organizations acknowledge gifts with verification notes and proof updates.
4. **Milestone & Growth Updates**: Ethical developmental progress updates for children under care.
5. **Separate User & Hidden Admin Portals**: Dedicated authentication flows with email verification for password resets.

---

## 🔐 Authentication & Security Architecture

### 1. Regular User Portal
- **Login Page**: [`/accounts/login/`](file:///c:/Users/HP/Documents/Avera%20project/templates/accounts/user_login.html)
  - Inputs: **Email address** and **Password**.
  - Includes a link: **"Reset Password?"**.
- **Registration Page**: [`/accounts/register/`](file:///c:/Users/HP/Documents/Avera%20project/templates/accounts/user_register.html)
  - Inputs: **First Name**, **Last Name**, **Email**, **Phone Number**, **Password**, **Confirm Password**, and **User Type / Role** (Donor, Prospective Adopter, Volunteer).
- **Password Reset**: [`/accounts/password-reset/`](file:///c:/Users/HP/Documents/Avera%20project/templates/accounts/user_password_reset.html)
  - User submits registered email address.
  - A secure, single-use token verification link is dispatched to their email.
  - User verifies email by opening the link and sets a new password.
  - *Dev/Demo Helper*: In development mode, the reset link is displayed in the terminal console and also on the confirmation page for instant testing.

---

### 2. Admin Portal (Restricted & Hidden Access)
> **Requirement**: *"admin login registration page should not be shown"*  
> The main website header, navbar, home page, and footer **do NOT show any links or buttons** to the Admin Login or Admin Registration page.

- **Admin Login (Direct Hidden URL)**: [`/admin-portal/login/`](file:///c:/Users/HP/Documents/Avera%20project/templates/accounts/admin_login.html)
  - Accessible only via direct URL.
  - Inputs: **Admin Email** and **Admin Password**.
  - Non-admin credentials receive access restriction errors.
- **Admin Registration (Hidden)**: [`/admin-portal/register/`](file:///c:/Users/HP/Documents/Avera%20project/templates/accounts/admin_register.html)
  - Inputs: **First Name**, **Last Name**, **Email**, **Phone Number**, **Password**, **Confirm Password**.
  - **Admin Authorization Passcode**: `AVERA_ADMIN_2026` (prevents unauthorized individuals from self-registering as admins).
- **Admin Password Reset**: [`/admin-portal/password-reset/`](file:///c:/Users/HP/Documents/Avera%20project/templates/accounts/admin_password_reset.html)
  - Verification link dispatched to admin email to set a new password.
- **Admin Management Dashboard**: [`/admin-portal/dashboard/`](file:///c:/Users/HP/Documents/Avera%20project/templates/core/admin_dashboard.html)
  - Manage gifts, update statuses, upload impact proof feedbacks, manage child profiles, and add wishlist campaigns.

---

## 🚀 Quick Start Guide

### 1. Run the Development Server
```bash
python manage.py runserver
```
Then open your browser at: `http://127.0.0.1:8000/`

### 2. Pre-seeded Demo Accounts
You can log in immediately using these pre-seeded accounts:

| Role | Email | Password | Access URL |
|---|---|---|---|
| **Supporter / Donor** | `donor@example.com` | `user123` | [`/accounts/login/`](http://127.0.0.1:8000/accounts/login/) (or Navbar "Log In") |
| **System Admin** | `admin@avera.org` | `admin123` | [`/admin-portal/login/`](http://127.0.0.1:8000/admin-portal/login/) *(Hidden URL)* |

### 3. Re-seed Demo Data (Optional)
If you ever want to reset or repopulate the sample data:
```bash
python manage.py seed_avera
```

### 4. Run Automated Tests
```bash
python manage.py test
```
All 11 unit & integration tests verify:
- User registration, login, and password reset email verification flow.
- Admin registration, login, and password reset email verification flow.
- Non-visibility of admin routes on public navigation.
- Gift pledging, wishlist progress tracking, and proof feedback loop.

---

## 🏛️ Class Diagram & Database Models (Slide 9 Mapping)

- `accounts.User`: Custom user model with email authentication (`first_name`, `last_name`, `email`, `phone`, `role`, `user_type`).
- `core.CareOrganization`: Organization details, verification status.
- `core.Child`: Alias, age, gender, health status, adoption status, and home organization.
- `core.AdoptionInformation`: Structured legal eligibility, required documents, process, and contacts.
- `core.Wishlist`: Item name, quantity needed, received, priority, status.
- `core.Gift`: Pledged by donor for organization/wishlist, tracking reference, and status.
- `core.Feedback`: Proof message and photo confirming gift handover.
- `core.MilestoneUpdate`: Periodic child progress updates.
- `core.SuccessStory`: Adoption stories and milestones.
- `core.FAQ`: Categorized FAQs.
- `core.Notification`: Donor notifications for gift updates and milestone reminders.

---

## 👥 Group 4 Presenters
- **Jannatul Ferdous Jyoti** (24101036)
- **Mahbuba Mim** (24101040)
- **Raisa Jerin** (24101045)
- **Mim Babu** (24101032)
- **Mst. Lamia Akter Jahan** (24101037)
