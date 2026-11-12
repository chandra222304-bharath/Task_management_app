from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Task


class TaskManagementTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Create two distinct test users for user-isolation testing
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='Password123!',
            first_name='Alice',
            last_name='Smith'
        )

        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='Password123!',
            first_name='Bob',
            last_name='Jones'
        )

        # Create sample tasks for user1
        self.task1 = Task.objects.create(
            user=self.user1,
            title='Prepare Financial Report',
            description='Analyze quarterly revenue and expenses',
            priority='High',
            status='Pending',
            start_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=5)
        )

        self.task2 = Task.objects.create(
            user=self.user1,
            title='Website Redesign Mockup',
            description='Create Figma wireframes',
            priority='Medium',
            status='In Progress',
            start_date=timezone.now().date() - timedelta(days=3),
            due_date=timezone.now().date() + timedelta(days=2)
        )

        # Create an overdue task for user1
        self.overdue_task = Task.objects.create(
            user=self.user1,
            title='Submit Tax Returns',
            description='File annual corporate taxes',
            priority='High',
            status='Pending',
            start_date=timezone.now().date() - timedelta(days=10),
            due_date=timezone.now().date() - timedelta(days=2)
        )

        # Create a task for user2 to test user-specific access
        self.bob_task = Task.objects.create(
            user=self.user2,
            title='Bob Secret Project',
            description='Confidential data',
            priority='Low',
            status='Pending',
            due_date=timezone.now().date() + timedelta(days=10)
        )

    # 1. Test User Registration
    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'charlie',
            'email': 'charlie@example.com',
            'first_name': 'Charlie',
            'last_name': 'Brown',
            'password': 'CharliePassword123!',
            'confirm_password': 'CharliePassword123!'
        })
        self.assertEqual(response.status_code, 302)  # Redirects to dashboard upon success
        self.assertTrue(User.objects.filter(username='charlie').exists())

    # 2. Test User Login and Logout
    def test_user_login_and_logout(self):
        # Login
        response = self.client.post(reverse('login'), {
            'username': 'alice',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)

        # Check authenticated session
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        # Logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

        # Dashboard should redirect to login when unauthenticated
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    # 3. Test Invalid Form Submissions
    def test_invalid_registration(self):
        # Mismatched passwords
        response = self.client.post(reverse('register'), {
            'username': 'invaliduser',
            'email': 'invalid@example.com',
            'password': 'Password123!',
            'confirm_password': 'MismatchPassword!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='invaliduser').exists())

    def test_invalid_task_dates(self):
        self.client.login(username='alice', password='Password123!')
        # Start date after due date
        response = self.client.post(reverse('task_create'), {
            'title': 'Bad Dates Task',
            'priority': 'Medium',
            'status': 'Pending',
            'start_date': (timezone.now().date() + timedelta(days=10)).isoformat(),
            'due_date': (timezone.now().date() + timedelta(days=2)).isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(title='Bad Dates Task').exists())

    # 4. Test Task Creation
    def test_create_task(self):
        self.client.login(username='alice', password='Password123!')
        response = self.client.post(reverse('task_create'), {
            'title': 'New Integration Test Task',
            'description': 'Ensure CI/CD passes',
            'priority': 'High',
            'status': 'In Progress',
            'start_date': timezone.now().date().isoformat(),
            'due_date': (timezone.now().date() + timedelta(days=7)).isoformat()
        })
        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title='New Integration Test Task')
        self.assertEqual(task.user, self.user1)

    # 5. Test Task Update
    def test_update_task(self):
        self.client.login(username='alice', password='Password123!')
        response = self.client.post(reverse('task_update', kwargs={'pk': self.task1.pk}), {
            'title': 'Prepare Financial Report (Updated)',
            'description': 'Updated description',
            'priority': 'High',
            'status': 'Completed',
            'start_date': self.task1.start_date.isoformat(),
            'due_date': self.task1.due_date.isoformat()
        })
        self.assertEqual(response.status_code, 302)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Prepare Financial Report (Updated)')
        self.assertEqual(self.task1.status, 'Completed')

    # 6. Test Task Deletion
    def test_delete_task(self):
        self.client.login(username='alice', password='Password123!')
        task_pk = self.task1.pk
        response = self.client.post(reverse('task_delete', kwargs={'pk': task_pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=task_pk).exists())

    # 7. Test User-Specific Task Access (User Isolation)
    def test_user_isolation(self):
        # Alice cannot view, edit, or delete Bob's task
        self.client.login(username='alice', password='Password123!')

        # Detail view should return 404
        response = self.client.get(reverse('task_detail', kwargs={'pk': self.bob_task.pk}))
        self.assertEqual(response.status_code, 404)

        # Update should return 404
        response = self.client.post(reverse('task_update', kwargs={'pk': self.bob_task.pk}), {
            'title': 'Hacked Title',
            'priority': 'High',
            'status': 'Completed'
        })
        self.assertEqual(response.status_code, 404)

        # Delete should return 404
        response = self.client.post(reverse('task_delete', kwargs={'pk': self.bob_task.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(pk=self.bob_task.pk).exists())

        # Bob's task must not appear in Alice's task list
        response = self.client.get(reverse('task_list'))
        self.assertNotContains(response, 'Bob Secret Project')

    # 8. Test Search and Filtering
    def test_search_and_filter(self):
        self.client.login(username='alice', password='Password123!')

        # Search by title
        response = self.client.get(reverse('task_list') + '?q=Financial')
        self.assertContains(response, 'Prepare Financial Report')
        self.assertNotContains(response, 'Website Redesign')

        # Filter by status
        response = self.client.get(reverse('task_list') + '?status=In+Progress')
        self.assertContains(response, 'Website Redesign')
        self.assertNotContains(response, 'Prepare Financial Report')

        # Filter by priority
        response = self.client.get(reverse('task_list') + '?priority=Medium')
        self.assertContains(response, 'Website Redesign')

        # Filter overdue tasks
        response = self.client.get(reverse('task_list') + '?overdue=1')
        self.assertContains(response, 'Submit Tax Returns')
        self.assertNotContains(response, 'Prepare Financial Report')

    # 9. Test Status Change Toggle
    def test_task_toggle_status(self):
        self.client.login(username='alice', password='Password123!')
        self.assertEqual(self.task1.status, 'Pending')
        self.client.get(reverse('task_toggle', kwargs={'pk': self.task1.pk}))
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'Completed')

    # 10. Test Overdue Property
    def test_overdue_property(self):
        self.assertTrue(self.overdue_task.is_overdue)
        self.assertFalse(self.task1.is_overdue)
