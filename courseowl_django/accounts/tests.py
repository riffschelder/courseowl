from django.test import TestCase
from django.test.client import Client
from accounts.models import UserProfile, User
from accounts.views import check_valid_password, valid_email_address, username_md5, unique_user


class AccountsTest(TestCase):
    def setUp(self):
        """
        Set up a demo user and user profile
        """
        self.client = Client()
        self.demo_user = User.objects.create_user(username='demo_user', email='demo@user.com', password='qwerty123',
                                                  first_name='', last_name='')
        self.user_profile = UserProfile(user=self.demo_user)

    def test_valid_email(self):
        """
        Tests for valid email format
        """
        self.assertFalse(valid_email_address(''))
        self.assertFalse(valid_email_address('testmail.cu'))
        self.assertFalse(valid_email_address('testmail%$#.com'))
        self.assertFalse(valid_email_address('test@#.com'))
        self.assertTrue(valid_email_address('test@mail.com'))

    def test_valid_password(self):
        """
        Test if password input is sufficient
        """
        too_short = 'short'
        blank = ''
        valid = 'qwerty123'

        self.assertFalse(check_valid_password(too_short, too_short))
        self.assertFalse(check_valid_password(blank, blank))
        self.assertFalse(check_valid_password(too_short, 'blah'))
        self.assertFalse(check_valid_password(blank, 'asdf'))
        self.assertTrue(check_valid_password(valid, valid))

    def test_unique_user(self):
        """
        Test if email to be signed up is unique
        """
        email1 = 'test1@xyz.com'
        email2 = 'test2@xyz.com'
        password = 'qwerty123'

        # Create the user in DB with email1
        User.objects.create_user(username_md5(email1), email1, password, first_name="", last_name="")

        user1_not_unique = unique_user(email1)  # email1 already exists, thus it is not unique
        user2_unique = unique_user(email2)
        self.assertFalse(user1_not_unique)
        self.assertTrue(user2_unique)

    def login_with_password(self, password):
        """
        test helper method login as demo_user with various passwords
        on success: logs in and returns true
        on failure: returns false
        """
        return self.client.login(username='demo_user', password=password)

    def test_change_password(self):
        """
        Change password should succeed only if password == password_confirm
        Once password is changed, user shouldn't be able to log in with old password
        """

        # user can log in
        self.assertTrue(self.login_with_password('qwerty123'))

        # user changes password
        self.client.post('/accounts/change_password/', data={'password': '123qwerty', 'password_confirm': '123qwerty'})

        # user can log in with new password, but not the old
        self.assertFalse(self.login_with_password('qwerty123'))
        self.assertTrue(self.login_with_password('123qwerty'))

        # user changes password but fails confirm
        self.client.post('/accounts/change_password/', data={'password': 'abc123def', 'password_confirm': 'qwerty123'})

        # user didn't change password; can still log in with old password
        self.assertFalse(self.login_with_password('abc123def'))
        self.assertFalse(self.login_with_password('qwerty123'))
        self.assertTrue(self.login_with_password('123qwerty'))

    def test_change_email(self):
        """
        Change email should succeed only if the new email is not empty and another user does not have the same email
        """

        # user can log in:
        login_successful = self.client.login(username='demo_user', password='qwerty123')
        self.assertTrue(login_successful)

        # user changes email successfully:
        self.client.post('/accounts/change_email/', data={'new_email': 'demo_new@user.com'})
        temp_user = User.objects.get(email='demo_new@user.com')
        self.assertEqual('demo_new@user.com', temp_user.email)

        # user changes email to empty string, so it is not changed:
        self.client.post('/accounts/change_email/', data={'new_email': ''})
        self.assertEqual('demo_new@user.com', temp_user.email)

        # user changes email to invalid email, so it is not changed:
        self.client.post('/accounts/change_email/', data={'new_email': 'i like cats'})
        self.assertEqual('demo_new@user.com', temp_user.email)

        # user changes email to existing email, so it is not changed:
        second_user = User.objects.create_user(username='799b18ba74e7439a7fbd03c0c1e6da', email='second@abc.com',
                                               password='qwerty123', first_name='', last_name='')
        second_user.save()
        second_user_profile = UserProfile(user=second_user)
        second_user_profile.save()

        self.client.post('/accounts/change_email/', data={'new_email': 'second@abc.com'})
        self.assertEqual('demo_new@user.com', temp_user.email)

    def test_deactivate_account(self):
        """
        User should not be able to login after deactivation
        """
        login_successful = self.client.login(username='demo_user', password='qwerty123')
        self.assertTrue(login_successful)

        response = self.client.get('/accounts/deactivate_account/')

        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.login(username='demo_user', password='qwerty123'))  # make sure user cannot log in
