from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task


class Command(BaseCommand):
    help = 'Seeds initial users and sample tasks for local testing'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with sample users and tasks...')

        # 1. Superuser / Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@taskflow.dev',
                'first_name': 'Vincent',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created superuser 'admin' with password 'admin123'"))
        else:
            self.stdout.write("Superuser 'admin' already exists.")

        # 2. Regular User (Alex)
        alex_user, created = User.objects.get_or_create(
            username='alex',
            defaults={
                'email': 'alex@taskflow.dev',
                'first_name': 'Alex',
                'last_name': 'Johnson'
            }
        )
        if created:
            alex_user.set_password('alex123')
            alex_user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user 'alex' with password 'alex123'"))

        # 3. Create Sample Tasks for Admin
        today = timezone.now().date()
        admin_sample_tasks = [
            {
                'title': 'Design User Interface for TaskFlow Mobile App',
                'description': 'Create comprehensive responsive wireframes, color tokens, and navigation flows in Figma.',
                'priority': 'High',
                'status': 'In Progress',
                'start_date': today - timedelta(days=2),
                'due_date': today + timedelta(days=3)
            },
            {
                'title': 'Q4 Infrastructure Security Audit & Penetration Testing',
                'description': 'Conduct penetration testing on API endpoints, review SSL certificates, and audit IAM permissions.',
                'priority': 'High',
                'status': 'Pending',
                'start_date': today,
                'due_date': today + timedelta(days=6)
            },
            {
                'title': 'Database Schema Optimization & Query Indexing',
                'description': 'Profile slow queries on task filters, add database indices for foreign keys and status columns.',
                'priority': 'Medium',
                'status': 'Completed',
                'start_date': today - timedelta(days=7),
                'due_date': today - timedelta(days=1)
            },
            {
                'title': 'Annual Corporate Income Tax Filing',
                'description': 'Consolidate audited financial statements and file tax returns with revenue department.',
                'priority': 'High',
                'status': 'Pending',
                'start_date': today - timedelta(days=14),
                'due_date': today - timedelta(days=2)  # Overdue!
            },
            {
                'title': 'Draft Employee Onboarding Documentation',
                'description': 'Write developer setup guides, Git branch conventions, and environment variable configuration handbook.',
                'priority': 'Low',
                'status': 'Completed',
                'start_date': today - timedelta(days=10),
                'due_date': today - timedelta(days=3)
            },
            {
                'title': 'Integrate Cloud Backup & Disaster Recovery Pipeline',
                'description': 'Automate daily encrypted database backups to off-site object storage with retention policies.',
                'priority': 'Medium',
                'status': 'In Progress',
                'start_date': today - timedelta(days=1),
                'due_date': today + timedelta(days=5)
            },
            {
                'title': 'Quarterly Customer Satisfaction & NPS Survey Analysis',
                'description': 'Aggregate user feedback survey results and prepare summary presentation for executive team.',
                'priority': 'Low',
                'status': 'Pending',
                'start_date': today,
                'due_date': today + timedelta(days=12)
            },
            {
                'title': 'Renew Domain Name Registrations & Cloudflare SSL',
                'description': 'Ensure auto-renewal of production domain names and DNS records verification.',
                'priority': 'High',
                'status': 'Completed',
                'start_date': today - timedelta(days=15),
                'due_date': today - timedelta(days=5)
            }
        ]

        for task_data in admin_sample_tasks:
            Task.objects.get_or_create(
                user=admin_user,
                title=task_data['title'],
                defaults=task_data
            )

        # 4. Create Sample Tasks for Alex (to demonstrate user isolation)
        alex_sample_tasks = [
            {
                'title': 'Alex Client Presentation Pitch Deck',
                'description': 'Prepare slides for Monday pitch to prospective partners.',
                'priority': 'High',
                'status': 'In Progress',
                'start_date': today - timedelta(days=1),
                'due_date': today + timedelta(days=2)
            },
            {
                'title': 'Alex Weekly Team Standup Notes',
                'description': 'Circulate weekly achievements and blockers summary.',
                'priority': 'Medium',
                'status': 'Completed',
                'start_date': today - timedelta(days=4),
                'due_date': today - timedelta(days=1)
            }
        ]

        for task_data in alex_sample_tasks:
            Task.objects.get_or_create(
                user=alex_user,
                title=task_data['title'],
                defaults=task_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with sample data!'))
