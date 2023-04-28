from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired


class ChangeUserForm(FlaskForm):
    nickname = StringField('Никнейм', validators=[DataRequired()])
    description = TextAreaField('Описание')
    email = EmailField('Почта', validators=[DataRequired()])
    old = PasswordField('Старый пароль', validators=[DataRequired()])
    password = PasswordField('Новый пароль(Если хотите изменить)')
    repeat = PasswordField('Повторить новый пароль')
    submit = SubmitField('Изменить')
