#!/usr/bin/env python3

from base import create_session, Base
from field import Field, Integer, String

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

User.drop_table()
Post.drop_table()
User.create_table()
Post.create_table()

user1 = User(name='user1', email='email1@mail.ru')
print(user1)

user1.save()
print(user1)

User.update(name = 'user2').filter(User.name == 'user1').call()
print(User.get().call())

result = User.get('id', 'name').filter(User.name == 'user2').call()
print(result)

post1 = Post(user_id=user1.id, post='hello')
post1.save()
print(Post.get().call())
print(User.get().call())

User.delete().filter(User.name == 'user2').call()
print(User.get().call())
