import sqlalchemy
from sqlalchemy import Column, orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    websites = orm.relationship("Website", backref='owner_user')
    help_in = orm.relationship("Website", secondary="users_to_websites", backref="helpers")
    id = Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    nickname = Column(sqlalchemy.String, nullable=True)
    email = Column(sqlalchemy.String, unique=True)
    hashed_password = Column(sqlalchemy.String, nullable=True)
    description = Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return self.nickname

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
