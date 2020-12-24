from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CreateCategory(FlaskForm):
    name_category = StringField('name_category', validators=[DataRequired(), Length(min=3, max=50)])
    slug_cat = StringField('slug_cat', validators=[DataRequired(), Length(min=3, max=255)])
    push_category = SubmitField('Submit')


class EditCategory(FlaskForm):
    name_category = StringField('name_category', validators=[DataRequired(), Length(min=3, max=50)])
    slug_cat = StringField('slug_cat', validators=[DataRequired(), Length(min=3, max=255)])
    push_category = SubmitField('Submit')
