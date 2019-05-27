#!/usr/bin/env python3

from base import create_session, Base
from field import Field, Integer, String, Relationship

session = create_session('test.db')
Base.set_session(session)

print(Integer)
print(String(200))

class User(Base):

    __tablename__ = 'users'

    id = Field(
        type=Integer,
        primary=True,
        autoincrement=True,
    )
    name = Field(
        type=String(100),
        not_null=True,
    )
    email = Field(
        type=String(100),
        not_null=True,
    )

class Post(Base):

    __tablename__ = 'posts'

    id = Field(
        type=Integer,
        primary=True,
        autoincrement=True,
    )
    user_id = Field(
        type=Integer,
        foreign=User.id,
    )
    post = Field(
        type=String(100),
        not_null=False,
    )

print(Post)

print([field[1].__dict__ for field in User.get_fields()])
print([field[1].__dict__ for field in Post.get_fields()])
User.drop_table()
Post.drop_table()
User.create_table()
Post.create_table()

user1 = User(name='user1', email='email1@mail.ru')
print(user1.__dict__)
print(User.get_fields_dict())

user1.save()
print(User.get())
print(user1.__dict__)
post1 = Post(user_id=user1.id, post='hello')
print(post1.__dict__)

