import sqlalchemy
from sqlalchemy import Column
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
association_table = sqlalchemy.Table(
    'websites_to_category',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('websites', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('websites.id')),
    sqlalchemy.Column('categories', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('categories.id'))
)


class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'categories'
    id = Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = Column(sqlalchemy.String, nullable=True)
