from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    nickname = StringField('Никнейм', validators=[DataRequired()])
    description = TextAreaField('Описание')
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    repeat = PasswordField('Повторить пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
