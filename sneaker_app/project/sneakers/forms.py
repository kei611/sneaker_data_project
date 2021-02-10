from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired


class AddSneakerForm(FlaskForm):
    sneaker_model_name = StringField('Sneaker Name', validators=[DataRequired()])
    sneaker_retail_price = IntegerField('Retail Price(JPY)', validators=[DataRequired()])
    sneaker_image = FileField('Sneaker Image', validators=[FileRequired()])
    sneaker_public = BooleanField('Public Sneaker', default="")

class EditSneakerForm(FlaskForm):
    sneaker_model_name = StringField('Sneaker Name', validators=[])
    sneaker_retail_price = IntegerField('Retail Price(JPY)', validators=[])
    sneaker_image = FileField('Sneaker Image')
    sneaker_public = BooleanField('Public Sneaker', default="")

class PredPriceForm(FlaskForm):
    sneaker_model_name = StringField('Sneaker Name', validators=[DataRequired()])
    sneaker_retail_price = IntegerField('Retail Price(JPY)', validators=[DataRequired()])
    sneaker_image = FileField('Sneaker Image', validators=[FileRequired()])
    sneaker_brand = SelectField('Brand', choices=[(0, 'Adidas')])
