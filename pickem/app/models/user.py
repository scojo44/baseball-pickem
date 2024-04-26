from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import bcrypt
from .helper import DBHelperMixin
from . import db, int_pk, str50, str_email, str_bcrypt_hash

class User(DBHelperMixin, db.Model):
    """A user playing the pickem game."""
    __tablename__ = 'users'

    id: Mapped[int_pk]
    email: Mapped[str_email] = mapped_column(unique=True)
    username: Mapped[str50] = mapped_column(unique=True)
    password: Mapped[str_bcrypt_hash]
    image_url: Mapped[Optional[str]] = mapped_column(default="/static/images/default-pic.png")
    header_image_url: Mapped[Optional[str]] = mapped_column(default="/static/images/warbler-hero.jpg")
    location: Mapped[Optional[str50]]

    # "Many" side of one-to-many relationships
    pick_sheets: Mapped[list['PickSheet']] = db.relationship(back_populates='user', cascade='all')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.  Hashes password and adds user to system."""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        user = User(username=username, email=email, password=hashed_pwd, image_url=image_url)

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

        if user:
            if bcrypt.check_password_hash(user.password, password):
                return user

        return False
