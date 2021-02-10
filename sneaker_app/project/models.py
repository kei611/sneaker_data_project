
from project import db, bcrypt, app
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from datetime import datetime
from werkzeug.utils import secure_filename
from wtforms import ValidationError
import os
 
class Sneaker(db.Model):
 
    __tablename__ = "sneakers"
 
    id = db.Column(db.Integer, primary_key=True)
    sneaker_model_name = db.Column(db.String, nullable=False)
    sneaker_retail_price = db.Column(db.Integer, nullable=False)
    is_public = db.Column(db.Boolean, nullable=False)
    image_filename = db.Column(db.String, default=None, nullable=True)
    image_url = db.Column(db.String, default=None, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, model_name, retail_price, user_id, is_public, image_filename=None, image_url=None):
        self.sneaker_model_name = model_name
        self.sneaker_retail_price = retail_price
        self.is_public = is_public
        self.image_filename = image_filename
        self.image_url = image_url
        self.user_id = user_id

    def __repr__(self):
        return '<id: {}, title: {}, user_id: {}>'.format(self.id, self.recipe_title, self.user_id)

    def import_form_data(self, request, form):
        """Import the data for this sneaker that was input via the EditSneakerForm
        class.  This can either be done by the user for the sneakers that they own
        or by the administrator.  Additionally, it is assumed that the form has
        already been validated prior to being passed in here."""
        try:
            if form.sneaker_model_name.data != self.sneaker_model_name:
                self.sneaker_model_name = form.sneaker_model_name.data

            if form.sneaker_retail_price.data != self.sneaker_retail_price:
                self.sneaker_retail_price = form.sneaker_retail_price.data

            if form.sneaker_public.data != self.is_public:
                self.is_public = form.sneaker_public.data

            if form.sneaker_image.has_file():
                file = request.files['sneaker_image']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOADS_DEFAULT_DEST'], filename))
                url = os.path.join(app.config['UPLOADS_DEFAULT_URL'], filename)
                self.image_filename = filename
                self.image_url = url

        except KeyError as e:
            raise ValidationError('Invalid sneaker: missing ' + e.args[0])
        return self


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=False)
    _password = db.Column(db.Binary(60), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    email_confirmation_sent_on = db.Column(db.DateTime, nullable=True)
    email_confirmed = db.Column(db.Boolean, nullable=True, default=False)
    email_confirmed_on = db.Column(db.DateTime, nullable=True)
    registered_on = db.Column(db.DateTime, nullable=True)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String, default='user')
    sneakers = db.relationship('Sneaker', backref='user', lazy='dynamic')

    def __init__(self, email, plaintext_password, email_confirmation_sent_on=None, role='user'):
        self.email = email
        self.password  = plaintext_password
        self.authenticated = False
        self.email_confirmation_sent_on = email_confirmation_sent_on
        self.email_confirmed = False
        self.email_confirmed_on = None
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = datetime.now()
        self.role = role

    @hybrid_property
    def password(self):
        return self._password
 
    @password.setter
    def password(self, plaintext_password):
        self._password = bcrypt.generate_password_hash(plaintext_password)

    @hybrid_method
    def is_correct_password(self, plaintext_password):
        return bcrypt.check_password_hash(self.password, plaintext_password)

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True
 
    @property
    def is_anonymous(self):
        """Always False, as anonymous users aren't supported."""
        return False
 
    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        """Requires use of Python 3"""
        return str(self.id)

    def __repr__(self):
        return '<User {0}>'.format(self.name)