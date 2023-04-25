from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired
from flask_login import current_user
from requests import get


class WebsiteForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    link = StringField('Ссылка', validators=[DataRequired()])
    description = TextAreaField('Описание')
    password = PasswordField('Пароль', validators=[DataRequired()])
    categories = SelectMultipleField('Категории', choices=get('http://127.0.0.1:8080/api/categories')
                                     .json()['categories'])
    choices = get('http://127.0.0.1:8080/api/users').json()['users']
    choices.pop(current_user)
    helpers = SelectMultipleField('Помощники', choices=choices)
    submit = SubmitField('Создать')
