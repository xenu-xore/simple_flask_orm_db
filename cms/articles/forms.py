from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length


class CreateCategory(FlaskForm):
    name_category = StringField('name_category', validators=[DataRequired(), Length(min=3, max=50)])
    slug_cat = StringField('slug_cat', validators=[DataRequired(), Length(min=3, max=255)])
    push_category = SubmitField('Submit')


class CreateArticle(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(min=3, max=50, message=u'Очень мало символов нужно '
                                                                                           u'больше 3-х')])
    short_description = StringField('short_description', validators=[DataRequired(), Length(min=3, max=50)])
    article = TextAreaField('article', validators=[DataRequired()])
    select_category = SelectField(u'Выбор категории', coerce=str, validators=[DataRequired()])
    slug_art = StringField('slug_art', validators=[DataRequired(), Length(min=3, max=255)])
    push_article = SubmitField('Submit')


class EditArticles(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(min=3, max=50, message=u'Очень мало символов нужно '
                                                                                           u'больше 3-х')])
    short_description = TextAreaField('short_description', validators=[DataRequired(), Length(min=3, max=50)])
    article = TextAreaField('article', validators=[DataRequired()])
    select_cat = SelectField(u'Выбор категории', coerce=str, validators=[DataRequired()])
    slug_art = StringField('slug_art', validators=[DataRequired(), Length(min=3, max=255)])
    push_article = SubmitField('Submit')