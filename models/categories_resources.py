from data.db_session import create_session
from data.categories import Category
from flask_restful import Resource, reqparse, abort
from flask import jsonify


def get_args(req=False):
    parser = reqparse.RequestParser()
    parser.add_argument('name', required=req)
    parser.add_argument('nested', default=False, type=bool)
    args = parser.parse_args()
    return args


def need_nested():
    parser = reqparse.RequestParser()
    parser.add_argument('nested', default=False, type=bool)
    args = parser.parse_args()
    return args['nested']


def abort_if_category_not_found(category_id):
    session = create_session()
    category = session.query(Category).get(category_id)
    if not category:
        abort(404, message=f"Category {category_id} not found")


def upgrade_category(category, args):
    if args['name'] is not None:
        category.name = args['name']
    return category


def nested_to_dict(category, need_nested):
    if need_nested:
        return (category.to_dict(rules=('-websites',)) |
                {'websites': [i.to_dict(rules=('-helpers', '-categories', '-owner_user')) for i in category.websites]})
    return category.to_dict(rules=('-websites',))


class CategoriesResource(Resource):
    def get(self, category_id):
        abort_if_category_not_found(category_id)
        session = create_session()
        category = session.query(Category).get(category_id)
        return jsonify({'category': nested_to_dict(category, need_nested())})

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
        nested = need_nested()
        return jsonify({'categories': [nested_to_dict(i, nested) for i in categories]})

    def post(self):
        args = get_args(req=True)
        session = create_session()
        category = upgrade_category(Category(), args)
        session.add(category)
        session.commit()
        return jsonify({'success': 'OK'})
