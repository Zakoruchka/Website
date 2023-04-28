from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired
from flask_login import current_user
from requests import get


class WebsiteForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    link = StringField('Ссылка', validators=[DataRequired()])
    description = TextAreaField('Описание')
    categories = SelectMultipleField('Категории')
    helpers = SelectMultipleField('Помощники')
    submit = SubmitField('Создать')

    def __init__(self):
        super().__init__()
        self.categories.choices = [(str(i['id']), i['name']) for i in get('http://127.0.0.1:8080/api/categories').json()['categories']]
        choices = [(str(i['id']), i['nickname']) for i in get('http://127.0.0.1:8080/api/users').json()['users']]
        if current_user:
            choices.remove((str(current_user.id), current_user.nickname))
        self.helpers.choices = choices
