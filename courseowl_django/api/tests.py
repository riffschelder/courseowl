from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from accounts.models import UserProfile
from courses.models import Subject, Course


class TestAPI(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='bob12345', email='bob@bob.com', password='bob123456', first_name='', last_name='')
        self.user.save()
        self.user_profile = UserProfile(user=self.user)
        self.user_profile.save()

    def test_json_subjects(self):
        temp_subject = Subject(name='Pottery')
        temp_subject.save()

        response = self.client.get('/api/subjects/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Pottery' in response.content)

    def test_json_courses(self):
        temp_course = Course(name='Advanced Pottery III')
        temp_course.save()

        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Advanced Pottery III' in response.content)

    def test_json_enrolled_courses(self):
        temp_course = Course(name='Advanced Pottery III', description='Learn pottery like you never imagined possible.',
                             instructor='Bob Smith')
        temp_course.save()

        self.user_profile.enrolled.add(temp_course)
        self.user_profile.save()

        login_successful = self.client.login(username='bob12345', password='bob123456')
        self.assertTrue(login_successful)

        response = self.client.get('/api/enrolled_courses/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual('["Advanced Pottery III"]', response.content)

    def test_json_liked_subjects(self):
        temp_subject = Subject(name='Computer Science')
        temp_subject.save()

        temp_subject_two = Subject(name='Computer Engineering')
        temp_subject_two.save()

        self.user_profile.interests.add(temp_subject)
        self.user_profile.interests.add(temp_subject_two)
        self.user_profile.save()

        login_successful = self.client.login(username='bob12345', password='bob123456')
        self.assertTrue(login_successful)
        response = self.client.get('/api/liked_subjects/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual('["Computer Science", "Computer Engineering"]', response.content)

    def test_json_like_subject(self):
        login_successful = self.client.login(username='bob12345', password='bob123456')
        self.assertTrue(login_successful)

        temp_subject = Subject(name='Pottery')
        temp_subject.save()
        response = self.client.post('/api/like_subject/', data={'liked_subject': 'Pottery'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('{"success": true}', response.content)
        response = self.client.post('/api/like_subject/', data={'liked_subject': 'Non-existent subject'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('{"success": false}', response.content)

    def test_json_sample_courses_for_subject(self):
        login_successful = self.client.login(username='bob12345', password='bob123456')
        self.assertTrue(login_successful)

        temp_subject = Subject(name='Pottery')
        temp_subject.save()
        temp_course = Course(name='Advanced Pottery I', description='Learn pottery I like you never imagined possible.',
                             instructor='Bob Smith')
        temp_course.save()
        temp_course.subjects.add(temp_subject)
        temp_course.save()
        temp_course_two = Course(name='Advanced Pottery II', description='Learn pottery II like you never imagined possible.',
                                 instructor='Carol Smith')
        temp_course_two.save()
        temp_course_two.subjects.add(temp_subject)
        temp_course_two.save()
        temp_course_three = Course(name='Advanced Pottery III', description='Learn pottery III like you never imagined possible.',
                                   instructor='Eve Smith')
        temp_course_three.save()
        temp_course_three.subjects.add(temp_subject)
        temp_course_three.save()

        response = self.client.post('/api/sample_courses/', data={'subject': 'Pottery'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('{"Advanced Pottery III": ["Learn pottery III like you never imagined possible.", null], "Advanced Pottery II": ["Learn pottery II like you never imagined possible.", null], "Advanced Pottery I": ["Learn pottery I like you never imagined possible.", null]}', response.content)

        response = self.client.post('/api/sample_courses/', data={'subject': 'Non-existent subject'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('{}', response.content)
