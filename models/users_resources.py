from data.db_session import create_session
from data.users import User
from data.websites import Website
from flask_restful import Resource, reqparse, abort
from flask import jsonify


def get_args(req=False):
    parser = reqparse.RequestParser()
    parser.add_argument('nickname', required=req)
    parser.add_argument('email', required=req)
    parser.add_argument('hashed_password', required=req)
    parser.add_argument('description', required=req)
    parser.add_argument('help_in', type=list[Website], required=False)
    parser.add_argument('websites', type=list[Website], required=False)
    args = parser.parse_args()
    return args


def abort_if_user_not_found(user_id):
    session = create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def upgrade_user(user, args):
    for i in ['nickname', 'email', 'hashed_password', 'description', 'websites', 'help_in']:
        if args[i] is not None:
            exec(f'user.{i} = args[\'{i}\']')
    return user


def second_to_dict(user):
    return (user.to_dict(rules=('-websites', '-help_in')) |
            {'help_in': [i.to_dict(rules=('-helpers', '-categories', '-owner_user')) for i in user.help_in]} |
            {'websites': [i.to_dict(rules=('-helpers', '-categories', '-owner_user')) for i in user.websites]})


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': second_to_dict(user)})

    def put(self, user_id):
        abort_if_user_not_found(user_id)
        args = get_args()
        if not args:
            abort(400, message="Empty request")
        session = create_session()
        upgrade_user(session.query(User).get(user_id), args)
        session.commit()
        return jsonify({'success': 'OK'})

    def post(self, user_id):
        abort_if_user_not_found(user_id)
        args = get_args(req=True)
        session = create_session()
        if session.query(User).get(user_id):
            abort(400, message=f"Id {user_id} already used")
        if session.query(User).filter(User.email == str(args['email'])).first():
            abort(400, message=f"Email {args['email']} already used")
        user = upgrade_user(User(id=user_id), args)
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = create_session()
        users = session.query(User).all()
        return jsonify({'users': [second_to_dict(i) for i in users]})

    def post(self):
        args = get_args(req=True)
        session = create_session()
        if session.query(User).filter(User.email == str(args['email'])).first():
            abort(400, message=f"Email {args['email']} already used")
        user = upgrade_user(User(), args)
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
