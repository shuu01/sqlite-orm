# sqlite-orm

Simple sqlite-based orm written for educational purpose.

Inspired by https://github.com/eaxdev/SQLite-ORM

- Supports select, delete, update queries.
- Supports create and delete queries.
- Supports query filter(now only '=', but it is possible to add any filter).
- Supports foreign keys.
- Support joins(always enable for table with foreign keys.

## usage

    from sqlite_orm import Base, Field, Integer, String, create_session

create session

    session = create_session('test.db')

put into base class

    Base.set_session(session)

create some tables

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

drop tables if exists

    User.drop_table()
    Post.drop_table()

create tables

    User.create_table()
    Post.create_table()

create user

    user1 = User(name='user1', email='email1@mail.ru')

look inside user object

    print(user1)
    >>> {'users.id': users.id, 'users.name': users.name, 'users.email': users.email}

save user into database

    user1.save()
    print(user1)
    >>> {'users.id': users.id, 'users.name': users.name, 'users.email': users.email}

update user

    User.update(name = 'user2').filter(User.name == 'user1').call()
    print(User.get().call())
    >>> [{'users_id': 1, 'users_name': 'user2', 'users_email': 'email1@mail.ru', 'posts_id': None, 'posts_user_id': None, 'posts_post': None}]

select user.id and user.name where name = 'user2'

    result = User.get('id', 'name').filter(User.name == 'user2').call()
    print(result)
    >>> [{'users_id': 1, 'users_name': 'user2'}]

create post

    post1 = Post(user_id=user1.id, post='hello')
    post1.save()
    print(Post.get().call())
    >>> [{'posts_id': 1, 'posts_user_id': 1, 'posts_post': 'hello'}]
    print(User.get().call())
    >>> [{'users_id': 1, 'users_name': 'user2', 'users_email': 'email1@mail.ru', 'posts_id': 1, 'posts_user_id': 1, 'posts_post': 'hello'}]

delete user with name = user2

    User.delete().filter(User.name == 'user2').call()
    print(User.get().call())
    >>> []
