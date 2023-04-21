from flask import Flask
from flask_restful import Api
from models.users_resources import UsersResource, UsersListResource
from models.websites_resource import WebsitesResource, WebsitesListResource
from data.db_session import global_init
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
api.add_resource(UsersResource, '/api/users/<int:user_id>')
api.add_resource(UsersListResource, '/api/users')
api.add_resource(WebsitesResource, '/api/websites/<int:website_id>')
api.add_resource(WebsitesListResource, '/api/websites')


def main():
    global_init("db/sites.db")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
