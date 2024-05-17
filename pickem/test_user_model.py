"""User model tests."""
# run these tests like:
#
#    python -m unittest test_user_model.py

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from app import create_app
from app.models import db, User

app = create_app()
app.testing = True

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
with app.app_context():
    db.create_all()

class UserModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            [db.session.delete(user) for user in User.get_all()]
            db.session.commit()

            mario = User.signup(username="mario", password="coin99")
            luigi = User.signup(username="luigi", password="mansion5")
            db.session.commit()
            
            self.mario_id = mario.id
            self.luigi_id = luigi.id

    def tearDown(self):
        """Clear any incomplete transactions."""
        with app.app_context():
            db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""
        user = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        with app.app_context():
            db.session.add(user)
            db.session.commit()

            self.assertEqual(user.username, "testuser")
            # User should have no messages & no followers
            # self.assertEqual(len(user.messages), 0)
            # self.assertEqual(len(user.followers), 0)

    def test_user_repr(self):
        """1. Does the repr method work as expected?"""
        with app.app_context():
            user1 = User.get(self.mario_id)
            user2 = User.get(self.luigi_id)
            self.assertEqual(f"{user1}", f"<User #{self.mario_id}: mario>")
            self.assertEqual(f"{user2}", f"<User #{self.luigi_id}: luigi>")
        
    def test_user_signup(self):
        """6. Does User.create successfully create a new user given valid credentials?"""
        with app.app_context():
            user = User.signup(username="zelda", password="triforce3")
            self.assertEqual(user.username, "zelda")
 
            db.session.add(user)
            db.session.commit()
 
            self.assertIsInstance(user, User)
            self.assertIsInstance(user.id, int)
            self.assertEqual(user.username, "zelda")
            self.assertIn("$2b$", user.password) # Check for bcrypt signature

    def test_user_signup_fail(self):
        """7. Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""
        with app.app_context():
            with self.assertRaises(IntegrityError):
                User.signup(username="mario", password="pipe123")
                db.session.commit()
                User.signup(username="yoshi", password="greendino5")
                db.session.commit()

    def test_user_authenticate(self):
        """8. Does User.authenticate successfully return a user when given a valid username and password?"""
        with app.app_context():
            user = User.authenticate("mario", "coin99")
            self.assertIsInstance(user, User)
            self.assertEqual(user.username, "mario")

    def test_user_auth_username_not_exist(self):
        """9. Does User.authenticate fail to return a user when the username is invalid?"""
        with app.app_context():
            user = User.authenticate("bowser", "peaches4")
            self.assertFalse(user)

    def test_user_auth_wrong_password(self):
        """10. Does User.authenticate fail to return a user when the password is invalid?"""
        with app.app_context():
            user = User.authenticate("mario", "triforce85")
            self.assertFalse(user)