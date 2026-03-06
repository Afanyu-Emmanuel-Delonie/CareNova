from datetime import date, time, timedelta
import uuid

from django.utils import timezone
from django.contrib.auth import get_user_model

from users.models import Profile, Category, DoctorProfile, PatientProfile
from appointments.models import Appointment, Review, AvailabilitySlot
from news.models import NewsArticle, ArticleParagraph, ArticleLike, ArticleComment
from chat.models import ChatGroup, Message, UserPresence, BlockedUser, PatientComplaint


User = get_user_model()


def ensure_user(email, password, role, **extras):
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "role": role,
            "is_verified": True,
            "is_staff": role == "ADMIN",
            "is_superuser": role == "ADMIN",
            **extras,
        },
    )
    if not created:
        user.role = role
        user.is_verified = True
        if role == "ADMIN":
            user.is_staff = True
            user.is_superuser = True
    user.set_password(password)
    user.save()
    return user


def ensure_profile(user, first_name, last_name, **extras):
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            **extras,
        },
    )
    if profile.first_name != first_name or profile.last_name != last_name:
        profile.first_name = first_name
        profile.last_name = last_name
        for key, value in extras.items():
            setattr(profile, key, value)
        profile.save()
    return profile


def main():
    # Admin
    admin_user = ensure_user(
        "afanyuemma@gail.com",
        "carenova",
        role="ADMIN",
    )
    ensure_profile(admin_user, "Afany", "Emma")

    # Categories
    cardiology, _ = Category.objects.get_or_create(name="Cardiology")
    dermatology, _ = Category.objects.get_or_create(name="Dermatology")

    # Doctors
    doc_user_1 = ensure_user("dr.amina@carenova.dev", "carenova", role="DOCTOR")
    doc_profile_1 = ensure_profile(doc_user_1, "Amina", "Yousif", phone_number="249900000001")
    doctor_1, _ = DoctorProfile.objects.get_or_create(
        profile=doc_profile_1,
        defaults={
            "category": cardiology,
            "specialization": "Cardiology",
            "years_experience": 8,
            "license_number": "LIC-CAR-0001",
            "bio": "Focused on preventive cardiology and lifestyle medicine.",
            "is_verified": True,
        },
    )

    doc_user_2 = ensure_user("dr.musa@carenova.dev", "carenova", role="DOCTOR")
    doc_profile_2 = ensure_profile(doc_user_2, "Musa", "Ali", phone_number="249900000002")
    doctor_2, _ = DoctorProfile.objects.get_or_create(
        profile=doc_profile_2,
        defaults={
            "category": dermatology,
            "specialization": "Dermatology",
            "years_experience": 5,
            "license_number": "LIC-DER-0002",
            "bio": "Skin health, dermatologic surgery, and patient education.",
            "is_verified": True,
        },
    )

    # Patient: Binyu Gillian
    patient_user = ensure_user("binyu.gillian@carenova.dev", "carenova", role="PATIENT")
    patient_profile = ensure_profile(
        patient_user,
        "Binyu",
        "Gillian",
        phone_number="249900000003",
        address="Khartoum, Sudan",
    )
    patient, _ = PatientProfile.objects.get_or_create(
        profile=patient_profile,
        defaults={
            "date_of_birth": date(1998, 5, 12),
            "blood_group": "O+",
            "allergies": "None known",
            "emergency_contact": "249900000004",
        },
    )

    # Presence
    for u in [admin_user, doc_user_1, doc_user_2, patient_user]:
        UserPresence.objects.get_or_create(user=u, defaults={"status": "ONLINE"})

    # Chat Group
    group, _ = ChatGroup.objects.get_or_create(
        name="Heart Health Support",
        defaults={
            "description": "Tips, questions, and support for heart health.",
            "created_by": admin_user,
        },
    )
    group.members.set([admin_user, doc_user_1, patient_user])

    # Messages
    Message.objects.get_or_create(
        sender=doc_user_1,
        receiver=patient_user,
        content="Hi Binyu, looking forward to our consultation.",
    )
    Message.objects.get_or_create(
        sender=patient_user,
        receiver=doc_user_1,
        content="Thanks doctor! I will share my symptoms during the call.",
    )
    Message.objects.get_or_create(
        sender=admin_user,
        group=group,
        content="Welcome everyone. Please be respectful and supportive.",
    )

    # Complaint + Block (sample data)
    PatientComplaint.objects.get_or_create(
        reported_by=doc_user_1,
        patient=patient_user,
        defaults={
            "description": "Patient missed two appointments without notice.",
            "status": "OPEN",
        },
    )
    BlockedUser.objects.get_or_create(
        blocked_by=doc_user_2,
        blocked_user=patient_user,
        defaults={"reason": "Test block for moderation demo."},
    )

    # News
    article, _ = NewsArticle.objects.get_or_create(
        title="5 Daily Habits to Protect Your Heart",
        defaults={
            "content": "A quick overview of simple habits that reduce cardiovascular risk.",
            "tags": "Health, Cardiology",
            "author": admin_user,
            "is_top_news": True,
        },
    )
    ArticleParagraph.objects.get_or_create(
        article=article,
        order=1,
        defaults={
            "subheading": "Move Every Day",
            "body": "Even 20 minutes of brisk walking can improve heart health.",
        },
    )
    ArticleParagraph.objects.get_or_create(
        article=article,
        order=2,
        defaults={
            "subheading": "Focus on Whole Foods",
            "body": "Prioritize vegetables, legumes, and whole grains.",
        },
    )
    ArticleLike.objects.get_or_create(article=article, user=patient_user)
    ArticleComment.objects.get_or_create(
        article=article,
        author=patient_user,
        body="Very helpful tips, thanks!",
    )

    # Availability
    base_date = timezone.now().date() + timedelta(days=1)
    for i, start_hour in enumerate([9, 10, 11, 12], start=1):
        AvailabilitySlot.objects.get_or_create(
            doctor=doctor_1,
            date=base_date + timedelta(days=i),
            start_time=time(start_hour, 0),
            defaults={"end_time": time(start_hour, 30), "is_booked": False},
        )

    # Recurring Appointments (4)
    recur_id = uuid.uuid4()
    for idx in range(1, 5):
        appt_date = base_date + timedelta(days=idx * 7)
        appt_time = time(10 + (idx - 1) % 2, 0)
        Appointment.objects.get_or_create(
            doctor=doctor_1,
            patient=patient,
            appointment_date=appt_date,
            appointment_time=appt_time,
            defaults={
                "is_emergency": False,
                "reason": "Follow-up for blood pressure management.",
                "clinical_notes": "Monitor BP at home; bring readings next visit.",
                "prescriptions": "Low-sodium diet; consider statin if labs confirm.",
                "status": "CONFIRMED",
                "is_recurring": True,
                "recurrence_group_id": recur_id,
                "occurrence_number": idx,
            },
        )

    # Completed appointment + Review
    completed_appt, _ = Appointment.objects.get_or_create(
        doctor=doctor_2,
        patient=patient,
        appointment_date=base_date,
        appointment_time=time(14, 0),
        defaults={
            "is_emergency": False,
            "reason": "Skin rash evaluation.",
            "clinical_notes": "Likely contact dermatitis.",
            "prescriptions": "Topical hydrocortisone for 7 days.",
            "status": "COMPLETED",
        },
    )
    Review.objects.get_or_create(
        appointment=completed_appt,
        doctor=doctor_2,
        patient=patient,
        defaults={"rating": 5, "comment": "Great consultation and clear guidance."},
    )

    print("Seed complete.")


if __name__ == "__main__":
    main()
