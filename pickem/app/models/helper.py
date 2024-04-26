from . import db

class DBHelperMixin:
    """Database methods common to all models.  Only make instances with subclasses."""
    @classmethod
    def get(cls, primary_key):
        """Return one instance of a model using the primary key or None if it doesn't exist."""
        return db.session.get(cls, primary_key)

    @classmethod
    def get_or_404(cls, primary_key):
        """Return one instance of a model using the primary key or a 404 error if it doesn't exist."""
        return db.get_or_404(cls, primary_key, description=f"{cls.__name__} {primary_key} doesn't exist.")

    @classmethod
    def get_first(cls, select = None):
        """Return the first of several instances of a model."""
        if select is None:
            select = db.select(cls)
        return db.session.scalars(select).first()

    @classmethod
    def get_all(cls, select = None):
        """Return all instances of a model."""
        if select is None:
            select = db.select(cls)
        return db.session.scalars(select).all()

    def save(self):
        """Save the model instance to the database.  Returns whether the save was successful.
        When False, find out what happened with get_last_error()."""
        db.session.add(self)
        try:
            db.session.commit()
            return True
        except Exception as error:
            db.session.rollback()
            self.last_error = error.args[0]
            return False
    
    def delete(self):
        """Delete a model instance from the database.  Returns whether the delete was successful.
        When False, find out what happened with get_last_error()."""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as error:
            db.session.rollback()
            self.last_error = error.args[0]
            return False
        
    last_error = None

    def get_last_error(self):
        """Call to get error details after a failure in save() or delete()."""
        error = self.last_error
        self.last_error = None
        return error
