from logging import getLogger

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserProfile

logger = getLogger(__name__)

class UserRegistrationTestCase(TestCase):
    """Test cases for user registration endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("user-registration")

    def test_user_registration_success(self):
        """Test successful user registration"""
        data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("refresh", response.data["tokens"])
        self.assertIn("access", response.data["tokens"])
        self.assertEqual(response.data["user"]["email"], data["email"])
        self.assertEqual(response.data["user"]["username"], data["username"])
        self.assertTrue(User.objects.filter(email=data["email"]).exists())

    def test_user_registration_passwords_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "TestPassword123",
            "password_confirm": "DifferentPassword123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=data["email"]).exists())

    def test_user_registration_weak_password(self):
        """Test registration with weak password"""
        data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "weak",
            "password_confirm": "weak",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=data["email"]).exists())

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user(
            email="testuser@example.com",
            username="existing",
            password="TestPassword123",
        )

        data = {
            "email": "testuser@example.com",
            "username": "newuser",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        User.objects.create_user(
            email="existing@example.com",
            username="testuser",
            password="TestPassword123",
        )

        data = {
            "email": "newuser@example.com",
            "username": "testuser",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_missing_required_fields(self):
        """Test registration with missing required fields"""
        data = {
            "email": "testuser@example.com",
            "username": "testuser",
            # Missing password
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_creates_profile(self):
        """Test that registration creates a user profile"""
        data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=data["email"])
        self.assertTrue(UserProfile.objects.filter(user=user).exists())


class UserLoginTestCase(TestCase):
    """Test cases for user login endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("user-login")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="TestPassword123",
        )
        self.user.is_verified = True
        self.user.save()
        UserProfile.objects.create(user=self.user)

    def test_user_login_success(self):
        """Test successful user login"""
        data = {"email": "testuser@example.com", "password": "TestPassword123"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("refresh", response.data["tokens"])
        self.assertIn("access", response.data["tokens"])
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {"email": "testuser@example.com", "password": "WrongPassword"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_unverified_user(self):
        """Test login with unverified user"""
        unverified_user = User.objects.create_user(
            email="unverified@example.com",
            username="unverified",
            password="TestPassword123",
        )
        unverified_user.is_verified = False
        unverified_user.save()

        data = {"email": "unverified@example.com", "password": "TestPassword123"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Account not verified. A new verification code has been sent to your email.",
            response.data["non_field_errors"][0],
        )

    def test_user_login_inactive_user(self):
        """Test login with inactive user"""
        inactive_user = User.objects.create_user(
            email="inactive@example.com",
            username="inactive",
            password="TestPassword123",
        )
        inactive_user.is_verified = True
        inactive_user.is_active = False
        inactive_user.save()

        data = {"email": "inactive@example.com", "password": "TestPassword123"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_nonexistent_email(self):
        """Test login with nonexistent email"""
        data = {"email": "nonexistent@example.com", "password": "TestPassword123"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_missing_email(self):
        """Test login without email"""
        data = {"password": "TestPassword123"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_missing_password(self):
        """Test login without password"""
        data = {"email": "testuser@example.com"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTestCase(TestCase):
    """Test cases for user profile endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse("user-profile")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="TestPassword123",
            first_name="Test",
            last_name="User",
        )
        self.user.is_verified = True
        self.user.save()
        self.profile = UserProfile.objects.create(user=self.user, bio="Original bio")

    def test_get_user_profile_authenticated(self):
        """Test retrieving user profile when authenticated"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["bio"], "Original bio")

    def test_get_user_profile_unauthenticated(self):
        """Test retrieving profile without authentication"""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_profile_no_profile_exists(self):
        """Test retrieving profile when profile doesn't exist"""
        new_user = User.objects.create_user(
            email="newuser@example.com",
            username="newuser",
            password="TestPassword123",
        )
        self.client.force_authenticate(user=new_user)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Profile should be created automatically
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())

    def test_update_user_profile_success(self):
        """Test successfully updating user profile"""
        self.client.force_authenticate(user=self.user)
        data = {"bio": "Updated bio"}
        response = self.client.put(self.profile_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], "Updated bio")

        # Verify update in database
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "Updated bio")

    def test_update_user_profile_partial(self):
        """Test partial update of user profile"""
        self.client.force_authenticate(user=self.user)
        data = {"bio": "New bio"}
        response = self.client.put(self.profile_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], "New bio")

    def test_update_user_profile_unauthenticated(self):
        """Test updating profile without authentication"""
        data = {"bio": "Updated bio"}
        response = self.client.put(self.profile_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile_creates_if_not_exists(self):
        """Test that profile is created if it doesn't exist during update"""
        new_user = User.objects.create_user(
            email="newuser@example.com",
            username="newuser",
            password="TestPassword123",
        )
        self.client.force_authenticate(user=new_user)
        data = {"bio": "New bio"}
        response = self.client.put(self.profile_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())

    def test_update_user_profile_empty_bio(self):
        """Test updating profile with empty bio"""
        self.client.force_authenticate(user=self.user)
        data = {"bio": ""}
        response = self.client.put(self.profile_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserChangePasswordTestCase(TestCase):
    """Test cases for user change password endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.change_password_url = reverse("user-change-password")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="OldPassword123",
        )
        self.user.is_verified = True
        self.user.save()

    def test_change_password_success(self):
        """Test successfully changing password"""
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "OldPassword123",
            "new_password": "NewPassword123",
            "confirm_new_password": "NewPassword123",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

        # Verify password changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123"))

    def test_change_password_incorrect_current(self):
        """Test changing password with incorrect current password"""
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "WrongPassword",
            "new_password": "NewPassword123",
            "confirm_new_password": "NewPassword123",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        """Test changing password with mismatched new passwords"""
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "OldPassword123",
            "new_password": "NewPassword123",
            "confirm_new_password": "DifferentPassword123",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_weak_password(self):
        """Test changing password to weak password"""
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "OldPassword123",
            "new_password": "weak",
            "confirm_new_password": "weak",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated(self):
        """Test changing password without authentication"""
        data = {
            "current_password": "OldPassword123",
            "new_password": "NewPassword123",
            "confirm_new_password": "NewPassword123",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_missing_fields(self):
        """Test changing password with missing fields"""
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "OldPassword123",
            # Missing new_password and confirm_new_password
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutTestCase(TestCase):
    """Test cases for user logout endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.logout_url = reverse("user-logout")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="TestPassword123",
        )
        self.user.is_verified = True
        self.user.save()
        self.refresh_token = str(RefreshToken.for_user(self.user))

    def test_logout_success(self):
        """Test successful user logout"""
        self.client.force_authenticate(user=self.user)
        data = {"refresh_token": self.refresh_token}
        response = self.client.post(self.logout_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_invalid_token(self):
        """Test logout with invalid refresh token"""
        self.client.force_authenticate(user=self.user)
        data = {"refresh_token": "invalid_token"}
        response = self.client.post(self.logout_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_unauthenticated(self):
        """Test logout without authentication"""
        data = {"refresh_token": self.refresh_token}
        response = self.client.post(self.logout_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_missing_token(self):
        """Test logout without providing refresh token"""
        self.client.force_authenticate(user=self.user)
        data = {}
        response = self.client.post(self.logout_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserListTestCase(TestCase):
    """Test cases for user list endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("users-list")

        # Create admin user
        self.admin = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="AdminPass123"
        )

        # Create regular users
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            username="user1",
            password="TestPassword123",
            is_verified=True,
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            username="user2",
            password="TestPassword123",
            is_verified=False,
        )

    def test_list_users_as_admin(self):
        """Test listing users as admin"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_list_users_as_non_admin(self):
        """Test listing users without admin permission"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_unauthenticated(self):
        """Test listing users without authentication"""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_filter_by_email(self):
        """Test filtering users by email"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url, {"email": "user1@example.com"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["email"], "user1@example.com")

    def test_list_users_filter_by_username(self):
        """Test filtering users by username"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url, {"username": "user1"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["username"], "user1")

    def test_list_users_filter_by_verification(self):
        """Test filtering users by verification status"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url, {"is_verified": True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user in response.data:
            self.assertTrue(user["is_verified"])


class UserDetailsTestCase(TestCase):
    """Test cases for user details endpoint"""

    def setUp(self):
        self.client = APIClient()

        # Create admin user
        self.admin = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="AdminPass123"
        )

        # Create a regular user
        self.user = User.objects.create_user(
            email="user@example.com",
            username="user",
            password="TestPassword123",
            is_verified=True,
        )

        self.details_url = reverse("user-details", args=[self.user.id])

    def test_get_user_details_as_admin(self):
        """Test retrieving user details as admin"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.details_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["username"], self.user.username)

    def test_get_user_details_as_non_admin(self):
        """Test retrieving user details without admin permission"""
        other_user = User.objects.create_user(
            email="other@example.com",
            username="other",
            password="TestPassword123",
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.get(self.details_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_details_unauthenticated(self):
        """Test retrieving user details without authentication"""
        response = self.client.get(self.details_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_details_nonexistent_user(self):
        """Test retrieving details of nonexistent user"""
        self.client.force_authenticate(user=self.admin)
        nonexistent_url = reverse("user-details", args=[99999])
        response = self.client.get(nonexistent_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_details_response_structure(self):
        """Test that user details response has correct structure"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.details_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        required_fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_verified",
            "date_joined",
            "last_login",
        ]
        for field in required_fields:
            self.assertIn(field, response.data)
