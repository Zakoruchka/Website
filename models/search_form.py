from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, SubmitField, StringField
from requests import get


class SearchForm(FlaskForm):
    text = StringField('Текст')
    categories = SelectMultipleField('Категории', choices=[
        i['name'] for i in get('http://127.0.0.1:5000/api/categories').json()['categories']])
    owner = SelectField('Владелец', choices=['Любой'] + [
        i['nickname'] for i in get('http://127.0.0.1:5000/api/users').json()['users']])
    submit = SubmitField('Найти')

    def __init__(self):
        super().__init__()
        self.categories.choices = [i['name'] for i in get('http://127.0.0.1:5000/api/categories').json()['categories']]
        self.owner.choices = ['Любой'] + [i['nickname'] for i in get('http://127.0.0.1:5000/api/users').json()['users']]
