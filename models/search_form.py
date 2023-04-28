from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, SubmitField, StringField
from requests import get


class SearchForm(FlaskForm):
    text = StringField('Текст')
    categories = SelectMultipleField('Категории')
    owner = SelectField('Владелец')
    submit = SubmitField('Найти')

    def __init__(self):
        super().__init__()
        self.categories.choices = [i['name'] for i in get('http://127.0.0.1:8080/api/categories').json()['categories']]
        self.owner.choices = ['Любой'] + [i['nickname'] for i in get('http://127.0.0.1:8080/api/users').json()['users']]
