from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Event, EventRegistration
from django.utils import timezone
from django.core import mail

User = get_user_model()

class EventTests(TestCase):

    def setUp(self):
        self.user1 = get_user_model().objects.create_user(username='user1', password='password')
        self.user2 = get_user_model().objects.create_user(username='user2', password='password')

        self.event = Event.objects.create(
            title="Test Event",
            description="This is a test event.",
            location="Test Location",
            date=timezone.now() + timezone.timedelta(days=1),
            organizer=self.user1
        )

    def test_index_view(self):
        response = self.client.get(reverse('events:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Event")
        self.assertTemplateUsed(response, 'events/index.html')

    def test_detail_view(self):
        response = self.client.get(reverse('events:detail', kwargs={'pk': self.event.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Event")
        self.assertContains(response, "This is a test event.")
        self.assertContains(response, "Test Location")
        self.assertContains(response, self.user1.username)
        self.assertTemplateUsed(response, 'events/detail.html')

    def test_event_registration(self):
        self.client.login(username='user2', password='password')
        response = self.client.post(reverse('events:register_for_event', kwargs={'event_id': self.event.pk}))
        self.assertRedirects(response, reverse('events:detail', kwargs={'pk': self.event.pk}))
        registration = EventRegistration.objects.filter(user=self.user2, event=self.event)
        self.assertTrue(registration.exists())
        self.assertEqual(registration.count(), 1)

    def test_create_event(self):
        self.client.login(username='user1', password='password')
        response = self.client.post(reverse('events:create'), {
            'title': 'New Event',
            'description': 'This is a new event.',
            'location': 'New Location',
            'date': timezone.now() + timezone.timedelta(days=1),
        })
        self.assertRedirects(response, reverse('events:detail', kwargs={'pk': 2}))
        new_event = Event.objects.get(title="New Event")
        self.assertEqual(new_event.organizer, self.user1)

    def test_update_event(self):
        self.client.login(username='user1', password='password')
        response = self.client.post(reverse('events:update', kwargs={'pk': self.event.pk}), {
            'title': 'Updated Event',
            'description': 'Updated description.',
            'location': 'Updated Location',
            'date': timezone.now() + timezone.timedelta(days=2),
        })
        self.assertRedirects(response, reverse('events:detail', kwargs={'pk': self.event.pk}))
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Updated Event")

    def test_update_event_not_owner(self):
        self.client.login(username='user2', password='password')
        response = self.client.get(reverse('events:update', kwargs={'pk': self.event.pk}))
        self.assertEqual(response.status_code, 403)

    def test_delete_event(self):
        self.client.login(username='user1', password='password')
        response = self.client.post(reverse('events:delete', kwargs={'pk': self.event.pk}))
        self.assertRedirects(response, reverse('events:index'))
        with self.assertRaises(Event.DoesNotExist):
            self.event.refresh_from_db()

    def test_delete_event_not_owner(self):
        self.client.login(username='user2', password='password')
        response = self.client.get(reverse('events:delete', kwargs={'pk': self.event.pk}))
        self.assertEqual(response.status_code, 403)

class EventSearchTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="password")
        Event.objects.create(title="Music Festival", description="An awesome music event", date=timezone.now(), organizer=self.user)
        Event.objects.create(title="Art Expo", description="Art and culture event", date=timezone.now(), organizer=self.user)

    def test_search_events(self):
        response = self.client.get(reverse('events:index'), {'q': 'Music'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Music Festival")
        self.assertNotContains(response, "Art Expo")

    def test_search_no_results(self):
        response = self.client.get(reverse('events:index'), {'q': 'Nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No events found.")

class EventEmailTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password', email='user1@example.com')
        self.user2 = User.objects.create_user(username='user2', password='password', email='user2@example.com')

        self.event = Event.objects.create(
            title="Test Event",
            description="A test event",
            date="2024-12-31 12:00:00",
            location="Test Location",
            organizer=self.user1
        )

    def test_event_registration_sends_email(self):
        self.client.login(username='user2', password='password')
        mail.outbox = []
        response = self.client.post(reverse('events:register_for_event', kwargs={'event_id': self.event.pk}))
        self.assertRedirects(response, reverse('events:detail', kwargs={'pk': self.event.pk}))
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertEqual(email.subject, f"Registration Confirmation for {self.event.title}")
        self.assertIn("You have successfully registered for Test Event", email.body)
        self.assertIn("Test Location", email.body)
        self.assertIn("2024-12-31", email.body)
        self.assertEqual(email.to, [self.user2.email])

    def test_no_email_if_already_registered(self):
        EventRegistration.objects.create(user=self.user2, event=self.event)
        self.client.login(username='user2', password='password')

        mail.outbox = []
        response = self.client.post(reverse('events:register_for_event', kwargs={'event_id': self.event.pk}))
        self.assertRedirects(response, reverse('events:detail', kwargs={'pk': self.event.pk}))
        self.assertEqual(len(mail.outbox), 0)
