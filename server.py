from flask import Flask, render_template, redirect
from flask_restful import Api
from flask_login import LoginManager, login_user
from models.users_resources import UsersResource, UsersListResource
from models.websites_resource import WebsitesResource, WebsitesListResource
from models.categories_resources import CategoriesResource, CategoriesListResource
from models.login_form import LoginForm
from models.register_form import RegisterForm
from data.users import User
from data.db_session import global_init, create_session
from requests import get
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)
api.add_resource(UsersResource, '/api/users/<int:user_id>')
api.add_resource(UsersListResource, '/api/users')
api.add_resource(WebsitesResource, '/api/websites/<int:website_id>')
api.add_resource(WebsitesListResource, '/api/websites')
api.add_resource(CategoriesResource, '/api/categories/<int:category_id>')
api.add_resource(CategoriesListResource, '/api/categories')
hostport = 'http://127.0.0.1:8080'
users_api = '/api/users'
websites_api = '/api/websites'
categories_api = '/api/categories'


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.query(User).get(user_id)


@app.route('/')
def main_window():
    websites = get(hostport + websites_api).json()['websites']
    print(websites)
    return render_template('main_window.html', title='Главная страница', websites=websites)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data == form.repeat.data:
            session = create_session()
            if not session.query(User).filter(User.email == str(form.email.data)).first():
                us = User(nickname=form.nickname.data, description=form.description.data, email=form.email.data)
                us.set_password(form.password.data)
                session.add(us)
                session.commit()
                login_user(us)
                return redirect("/")
            return render_template('register.html', message="Такая почта уже использована",
                                   title='Регистрация', form=form)
        return render_template('register.html', message="Пароли не совпадают", title='Регистрация', form=form)
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = create_session()
        user = session.query(User).filter(User.email == str(form.email.data)).first()
        if user and user.check_password(form.hashed_password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", title='Авторизация', form=form)
    return render_template('login.html', title='Авторизация', form=form)


def main():
    global_init("db/sites.db")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
