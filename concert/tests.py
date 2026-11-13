from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Concert, ConcertAttending

class BandFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testfan',password='TestOnlyPassword42')
        self.concert = Concert.objects.create(concert_name='Demo concert',duration=2,city='Almaty')

    def test_anonymous_cannot_book(self):
        response=self.client.post(reverse('concert_attendee'),{'concert_id':self.concert.pk,'attendee_choice':'Attending'})
        self.assertEqual(response.status_code,302)
        self.assertFalse(ConcertAttending.objects.exists())

    def test_login_and_update_attendance(self):
        response=self.client.post(reverse('login'),{'username':'testfan','password':'TestOnlyPassword42'})
        self.assertEqual(response.status_code,302)
        for status in ('Attending','Not Attending'):
            self.client.post(reverse('concert_attendee'),{'concert_id':self.concert.pk,'attendee_choice':status})
            self.assertEqual(ConcertAttending.objects.get().attending,status)
        self.assertEqual(ConcertAttending.objects.count(),1)
        self.assertContains(self.client.get(reverse('concerts')),'Demo concert')

    def test_reject_invalid_attendance(self):
        self.client.force_login(self.user)
        response=self.client.post(reverse('concert_attendee'),{'concert_id':self.concert.pk,'attendee_choice':'Invalid'})
        self.assertEqual(response.status_code,400)
        self.assertFalse(ConcertAttending.objects.exists())

    def test_signup_hashes_password_and_logs_in(self):
        self.client.post(reverse('signup'),{'username':'newfan','password':'TestOnlyPassword42'})
        self.assertTrue(User.objects.get(username='newfan').check_password('TestOnlyPassword42'))
        self.assertEqual(self.client.get(reverse('concerts')).status_code,200)

    def test_duplicate_signup_shows_error(self):
        response=self.client.post(reverse('signup'),{'username':'testfan','password':'TestOnlyPassword42'})
        self.assertContains(response,'already in use')
        self.assertEqual(User.objects.count(),1)
