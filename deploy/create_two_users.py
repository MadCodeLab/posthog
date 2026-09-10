from posthog.models import User, Organization, OrganizationMembership, Team

org = Organization.objects.first()
team = org.teams.first()

accounts = [
    {"email": "dangquochung.ptit@gmail.com", "name": "Dang Quoc Hung"},
    {"email": "lehai30042004@gmail.com", "name": "Le Hai"}
]

default_password = "Posthog@2026!"

for acc in accounts:
    email = acc["email"]
    name = acc["name"]
    user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.create_and_join(
            organization=org,
            email=email,
            password=default_password,
            first_name=name,
            level=OrganizationMembership.Level.ADMIN
        )
        user.is_email_verified = True
        user.is_active = True
        user.current_team = team
        user.save()
        print(f"Created user: {email} successfully!")
    else:
        user.set_password(default_password)
        user.is_email_verified = True
        user.is_active = True
        user.current_team = team
        user.save()
        m = OrganizationMembership.objects.filter(user=user, organization=org).first()
        if not m:
            OrganizationMembership.objects.create(user=user, organization=org, level=OrganizationMembership.Level.ADMIN)
        else:
            m.level = OrganizationMembership.Level.ADMIN
            m.save()
        print(f"Updated user: {email} successfully!")
