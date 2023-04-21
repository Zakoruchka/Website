from data.db_session import create_session
from data.categories import Category
from flask_restful import Resource, reqparse, abort
from flask import jsonify


def get_args(req=False):
    parser = reqparse.RequestParser()
    parser.add_argument('nickname', required=req)
    parser.add_argument('email', required=req)
    parser.add_argument('hashed_password', required=req)
    parser.add_argument('description', required=req)
    args = parser.parse_args()
    return args


def abort_if_category_not_found(category_id):
    session = create_session()
    category = session.query(Category).get(category_id)
    if not category:
        abort(404, message=f"Category {category_id} not found")


def upgrade_category(category, args):
    for i in ['nickname', 'email', 'hashed_password', 'description']:
        if args[i] is not None:
            exec(f'category.{i} = args[\'{i}\']')
    return category


def second_to_dict(category):
    return (category.to_dict(rules=('-websites', '-help_in')) |
            {'help_in': [i.to_dict(rules=('-helpers', '-categories', '-owner_category')) for i in category.help_in]} |
            {'websites': [i.to_dict(rules=('-helpers', '-categories', '-owner_category')) for i in category.websites]})


class CategoriesResource(Resource):
    def get(self, category_id):
        abort_if_category_not_found(category_id)
        session = create_session()
        category = session.query(Category).get(category_id)
        return jsonify({'category': second_to_dict(category)})

    def put(self, category_id):
        abort_if_category_not_found(category_id)
        args = get_args()
        if not args:
            abort(400, message="Empty request")
        session = create_session()
        upgrade_category(session.query(Category).get(category_id), args)
        session.commit()
        return jsonify({'success': 'OK'})

    def post(self, category_id):
        abort_if_category_not_found(category_id)
        args = get_args(req=True)
        session = create_session()
        if session.query(Category).get(category_id):
            abort(400, message=f"Id {category_id} already used")
        if session.query(Category).filter(Category.email == str(args['email'])).first():
            abort(400, message=f"Email {args['email']} already used")
        category = upgrade_category(Category(id=category_id), args)
        session.add(category)
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, category_id):
        abort_if_category_not_found(category_id)
        session = create_session()
        category = session.query(Category).get(category_id)
        session.delete(category)
        session.commit()
        return jsonify({'success': 'OK'})


class CategoriesListResource(Resource):
    def get(self):
        session = create_session()
        categories = session.query(Category).all()
        return jsonify({'categories': [second_to_dict(i) for i in categories]})

    def post(self):
        args = get_args(req=True)
        session = create_session()
        if session.query(Category).filter(Category.email == str(args['email'])).first():
            abort(400, message=f"Email {args['email']} already used")
        category = upgrade_category(Category(), args)
        session.add(category)
        session.commit()
        return jsonify({'success': 'OK'})
