from data.db_session import create_session
from data.websites import Website
from data.users import User
from data.categories import Category
from flask_restful import Resource, reqparse, abort
from flask import jsonify


def get_args(req=False):
    parser = reqparse.RequestParser()
    parser.add_argument('name', required=req)
    parser.add_argument('link', required=req)
    parser.add_argument('description', required=req)
    parser.add_argument('owner', type=int, required=req)
    parser.add_argument('helpers', type=int, action='append', required=False)
    parser.add_argument('categories', type=int, action='append', required=False)
    args = parser.parse_args()
    return args


def abort_if_website_not_found(website_id):
    session = create_session()
    website = session.query(Website).get(website_id)
    if not website:
        abort(404, message=f"Website {website_id} not found")


def upgrade_website(website, args, session):
    for i in ['name', 'link', 'description', 'owner']:
        if args[i] is not None:
            exec(f'website.{i} = args[\'{i}\']')
    if args['categories'] is not None:
        website.categories = [session.query(Category).get(i) for i in args['categories']]
    if args['helpers'] is not None:
        website.helpers = [session.query(User).get(i) for i in args['helpers']]
    return website


def nested_to_dict(website):
    return (website.to_dict(rules=('-categories', '-helpers', '-owner_user', '-owner')) |
            {'categories': [i.to_dict(rules=('-websites',)) for i in website.categories]} |
            {'helpers': [i.to_dict(rules=('-websites', '-help_in')) for i in website.helpers]} |
            {'owner_user': website.owner_user.to_dict(rules=('-websites', '-help_in'))})


class WebsitesResource(Resource):
    def get(self, website_id):
        abort_if_website_not_found(website_id)
        session = create_session()
        website = session.query(Website).get(website_id)
        return jsonify({'website': nested_to_dict(website)})

    def put(self, website_id):
        abort_if_website_not_found(website_id)
        args = get_args()
        if not args:
            abort(400, message="Empty request")
        session = create_session()
        upgrade_website(session.query(Website).get(website_id), args, session)
        session.commit()
        return jsonify({'success': 'OK'})

    def post(self, website_id):
        abort_if_website_not_found(website_id)
        args = get_args(req=True)
        session = create_session()
        if session.query(Website).get(website_id):
            abort(400, message=f"Id {website_id} already used")
        website = upgrade_website(Website(id=website_id), args, session)
        session.add(website)
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, website_id):
        abort_if_website_not_found(website_id)
        session = create_session()
        website = session.query(Website).get(website_id)
        session.delete(website)
        session.commit()
        return jsonify({'success': 'OK'})


class WebsitesListResource(Resource):
    def get(self):
        session = create_session()
        websites = session.query(Website).all()
        return jsonify({'websites': [nested_to_dict(i) for i in websites]})

    def post(self):
        args = get_args(req=True)
        session = create_session()
        website = upgrade_website(Website(), args, session)
        session.add(website)
        session.commit()
        return jsonify({'success': 'OK'})
