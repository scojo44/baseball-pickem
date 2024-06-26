"""The User model."""
from datetime import date
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import bcrypt
from .helper import DBHelperMixin
from . import db, int_pk, str50, str_email, str_bcrypt_hash

class User(DBHelperMixin, db.Model):
    """A user playing the pickem game."""
    __tablename__ = 'users'

    id: Mapped[int_pk]
    username: Mapped[str50] = mapped_column(unique=True)
    password: Mapped[str_bcrypt_hash]
    image_url: Mapped[Optional[str]]
    # Might add this back later
    # email: Mapped[str_email] = mapped_column(unique=True)

    # "Many" side of one-to-many relationships
    picks: Mapped[list['Pick']] = relationship(back_populates='user', cascade='all')

    def __repr__(self):
        """String representation of a user."""
        return f"<User #{self.id}: {self.username}>"

    @property
    def correct_picks(self, day = None):
        """Returns the user's correct picks, optionally filtering to just the date
        specified by day."""
        if day:
            return [p for p in self.picks if p.is_correct and day == p.game.start_time.date()]
        else: # Return picks from all time
            return [p for p in self.picks if p.is_correct]

    def change_password(self, new_password):
        """Change the user's password to new_password."""
        self.password = bcrypt.generate_password_hash(new_password).decode('UTF-8')

    @classmethod
    def signup(cls, username, password, image_url = None):
        """Sign up user.  Hashes password and adds user to system."""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        user = User(username=username, password=hashed_pwd, image_url=image_url)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """
        user = User.get_first(db.select(cls).where(User.username == username))

        if user and bcrypt.check_password_hash(user.password, password):
            return user

        return False
