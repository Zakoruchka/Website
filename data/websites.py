import sqlalchemy
from sqlalchemy import Column, orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
association_table = sqlalchemy.Table(
    'users_to_websites',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('users', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('websites', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('websites.id'))
)


class Website(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'websites'
    categories = orm.relationship("Category", secondary="websites_to_category", backref="websites")
    id = Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = Column(sqlalchemy.String, nullable=True)
    link = Column(sqlalchemy.String, nullable=True)
    description = Column(sqlalchemy.String, nullable=True)
    owner = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=True)
