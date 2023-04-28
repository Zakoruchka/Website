from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models.login_form import LoginForm
from models.register_form import RegisterForm
from models.search_form import SearchForm
from models.website_form import WebsiteForm
from models.change_user_form import ChangeUserForm
from data.users import User
from data.websites import Website
from data.categories import Category
from data.db_session import global_init, create_session
from requests import get, put
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
api_port = 'http://127.0.0.1:5000'
users_api = '/api/users'
websites_api = '/api/websites'
categories_api = '/api/categories'
meta_websites = False


def hash_password(password):
    return generate_password_hash(password)


def check_password(hashed_password, password):
    return check_password_hash(hashed_password, password)


def filter_websites(websites, form):
    if form.text.data:
        websites = filter(lambda z: form.text.data in z['name'] or form.text.data in z['description'], websites)
    if form.categories.data:
        websites = filter(lambda z: all(i in [j['name'] for j in z['categories']] for i in form.categories.data),
                          websites)
    if form.owner.data != 'Любой':
        websites = filter(lambda z: form.owner.data in z['owner_user']['nickname'], websites)
    return websites


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def main_window():
    global meta_websites
    form = SearchForm()
    websites = meta_websites if meta_websites else get(api_port + websites_api).json()['websites']
    if form.validate_on_submit():
        meta_websites = filter_websites(get(api_port + websites_api).json()['websites'], form)
        return redirect('/')
    meta_websites = False
    return render_template('main_window.html', title='Главная страница', websites=websites, form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data == form.repeat.data:
            if not any(map(lambda z: z['email'] == form.email.data or z['nickname'] in [form.nickname.data, 'Любой'],
                           get(api_port + users_api).json()['users'])):
                us = User(nickname=form.nickname.data, description=form.description.data, email=form.email.data)
                us.set_password(form.password.data)
                session = create_session()
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
        session.close()
        if user and user.check_password(form.hashed_password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", title='Авторизация', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/websites/<int:website_id>')
def choose_website(website_id):
    website = get(api_port + websites_api + f'/{website_id}').json()['website']
    return render_template('website.html', title=website['name'], website=website)


@app.route('/users/<int:user_id>')
def choose_user(user_id):
    user = get(api_port + users_api + f'/{user_id}').json()['user']
    return render_template('user.html', title=user['nickname'], user=user)


@app.route('/websites', methods=['GET', 'POST'])
@login_required
def add_website():
    form = WebsiteForm()
    if form.validate_on_submit():
        if not any(map(lambda z: z['link'] == form.link.data, get(api_port + websites_api).json()['websites'])):
            webs = Website(name=form.name.data, link=form.link.data, description=form.description.data,
                           owner=current_user.id)
            session = create_session()
            for i in form.categories.data:
                webs.categories.append(session.query(Category).get(i))
            for i in form.helpers.data:
                webs.helpers.append(session.query(User).get(i))
            session.add(webs)
            session.commit()
            return redirect("/")
        return render_template('create_website.html', message="Такая ссылка уже есть",
                               title='Добавление сайта', form=form)
    return render_template('create_website.html', title='Добавление сайта', form=form)


@app.route('/websites/change/<int:website_id>', methods=['GET', 'POST'])
@login_required
def change_website(website_id):
    website = get(api_port + websites_api + f'/{website_id}').json()['website']
    if current_user.id != website['owner_user']['id']:
        return redirect('/')
    form = WebsiteForm()
    if request.method == "GET":
        for i in ['name', 'link', 'description']:
            exec(f'form.{i}.data = website["{i}"]')
        for i in ['categories', 'helpers']:
            exec(f'form.{i}.data = [str(i["id"]) for i in website["{i}"]]')
    if form.validate_on_submit():
        if not any(map(lambda z: z['link'] == form.link.data and z['id'] != website_id, get(api_port + websites_api).json()['websites'])):
            params = {}
            for i in ['name', 'link', 'description', 'categories', 'helpers']:
                exec(f'params["{i}"] = form.{i}.data')
            put(api_port + websites_api + f'/{website_id}', json=params)
            return redirect(f'/websites/{website_id}')
        return render_template('create_website.html', message="Такая ссылка уже есть", title='Изменение сайта', form=form)
    return render_template('create_website.html', title='Изменение сайта', form=form)


@app.route('/users/change/<int:user_id>', methods=['GET', 'POST'])
@login_required
def change_user(user_id):
    if current_user.id != user_id:
        return redirect('/')
    form = ChangeUserForm()
    user = get(api_port + users_api + f'/{user_id}').json()['user']
    if request.method == "GET":
        for i in ['nickname', 'description', 'email']:
            exec(f'form.{i}.data = user["{i}"]')
    if form.validate_on_submit():
        if check_password(user['hashed_password'], form.old.data):
            if form.password.data == form.repeat.data:
                if not (any(map(lambda z: (z['email'] == form.email.data or form.nickname.data in
                                           [z['nickname'], 'Любой'])
                                and z['id'] != user_id, get(api_port + users_api).json()['users']))):
                    params = {}
                    for i in ['nickname', 'description', 'email']:
                        exec(f'params["{i}"] = form.{i}.data')
                    if form.password.data:
                        params['hashed_password'] = hash_password(form.password.data)
                    put(api_port + users_api + f'/{user_id}', json=params)
                    return redirect("/")
                return render_template('register.html', message="Такая почта или имя уже использованы",
                                       title='Изменение пользователя', form=form)
            return render_template('register.html', message="Новые пароли не совпадают", title='Изменение пользователя',
                                   form=form)
        return render_template('register.html', message="Неверный старый пароль", title='Изменение пользователя',
                               form=form)
    return render_template('register.html', title='Изменение пользователя', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    global_init("db/sites.db")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
