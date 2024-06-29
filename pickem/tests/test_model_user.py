"""User model tests."""
from sqlalchemy.exc import IntegrityError
from app.models import db, User
from .base import PickemTestCase

class UserModelTestCase(PickemTestCase):
    """User Model Tests."""
    def test_constructor(self):
        """Test the basic model."""
        user = User(
            username="testuser",
            password="HASHED_PASSWORD"
        )

        with self.app.app_context():
            db.session.add(user)
            db.session.commit()

            self.assertEqual(user.username, "testuser")
            self.assertEqual(len(user.picks), 0) # User should have no picks

    def test_repr(self):
        """Test the __repr__ method."""
        with self.app.app_context():
            user1 = User.get(self.mario_id)
            user2 = User.get(self.luigi_id)
            self.assertEqual(f"{user1}", f"<User #{self.mario_id}: mario>")
            self.assertEqual(f"{user2}", f"<User #{self.luigi_id}: luigi>")

    def test_signup(self):
        """Test user the signup process."""
        with self.app.app_context():
            user = User.signup(username="zelda", password="triforce3")
            self.assertEqual(user.username, "zelda")
 
            db.session.add(user)
            db.session.commit()
 
            self.assertIsInstance(user, User)
            self.assertIsInstance(user.id, int)
            self.assertEqual(user.username, "zelda")
            self.assertFalse(user.is_admin)
            self.assertIn("$2b$", user.password) # Check for bcrypt signature

    def test_signup_admin(self):
        """Test user the signup process."""
        with self.app.app_context():
            admin = User.signup(username="link", password="excuse-me-princess", is_admin=True)
            self.assertEqual(admin.username, "link")
 
            db.session.add(admin)
            db.session.commit()
 
            self.assertIsInstance(admin, User)
            self.assertIsInstance(admin.id, int)
            self.assertEqual(admin.username, "link")
            self.assertTrue(admin.is_admin)
            self.assertIn("$2b$", admin.password) # Check for bcrypt signature

    def test_signup_fail(self):
        """ Test signup validation with invalid data."""
        with self.app.app_context():
            with self.assertRaises(IntegrityError):
                User.signup(username="mario", password="pipe123")
                db.session.commit()
            db.session.rollback()

    def test_authenticate(self):
        """Test whether a user is returned when given a correct username and password."""
        with self.app.app_context():
            user = User.authenticate("mario", "99coins")
            self.assertNotEqual(user, False)
            self.assertIsInstance(user, User)
            self.assertEqual(user.username, "mario")

    def test_auth_username_not_exist(self):
        """Test whether a user is not returned when the username doesn't exist."""
        with self.app.app_context():
            user = User.authenticate("bowser", "peaches4")
            self.assertFalse(user)

    def test_auth_wrong_password(self):
        """Test whether a user is not returned when the password is wrong."""
        with self.app.app_context():
            user = User.authenticate("mario", "triforce85")
            self.assertFalse(user)

    def test_change_password(self):
        """Can the password be changed?"""
        with self.app.app_context():
            # Log in the user and change the password
            user1 = User.authenticate("mario", "99coins")
            user1.change_password("1up1up1up")
            # Log in the same user with the new password
            user2 = User.authenticate('mario', '1up1up1up')
            self.assertNotEqual(user2, False)
            self.assertIsInstance(user2, User)
            self.assertEqual(user2.username, 'mario')
