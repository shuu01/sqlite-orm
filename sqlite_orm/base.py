from .field import Field
from .query import Query


class MetaBase(type):
    # metaclass magic, that set table class attribute for every field in this class
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, Field):
                attr_value.set_table_class(cls)
                if attr_value.foreign:
                    attr_value.foreign.__setattr__('_fk', cls)


class Base(metaclass=MetaBase):

    _session = None # session inside class
    __tablename__ = None

    def __init__(self, **kwargs):
        super().__init__()
        for field_name, field_instance in self.__class__.get_fields():
            self.__setattr__(field_name, kwargs.get(field_name, field_instance.default_value))

    def __repr__(self):

        return str(self.get_fields_dict())

    @classmethod
    def get_tablename(cls):

        return cls.__tablename__

    @classmethod
    def set_session(cls, session):

        cls._session = session

    @classmethod
    def get_session(cls):

        if cls._session is not None:
            return cls._session
        else:
            raise Exception('Cannot get session.')

    @classmethod
    def get_cursor(cls):

        return cls.get_session().cursor()

    @classmethod
    def get_field_name(cls, field):

        for name, instance in cls.__dict__.items():
            if instance is field:
                return name

    @classmethod
    def get_field_by_name(cls, name):

        return cls.__dict__.get(name)

    @classmethod
    def get_fields(cls):

        for name, field in cls.__dict__.items():
            if isinstance(field, Field):
                yield name, field


    def get_fields_dict(self):

        return {
            name: field.__class__.value(getattr(self, name))
            for name, field in self.__class__.get_fields()
        }


    @classmethod
    def get_foreign_field_by_table(cls, table):

        for name, field in cls.get_fields():
            if field.foreign and field.foreign.table_class is table:
                return field


    @classmethod
    def create_table(cls):

        query = Query().create_table(cls).query
        cls.get_cursor().execute(query)


    @classmethod
    def drop_table(cls):

        query = Query().drop_table(cls).query
        cls.get_cursor().execute(query)


    @classmethod
    def get(cls, *args):

        query = Query().get(cls, *args)
        return query

    @classmethod
    def update(cls, **kwargs):

        query = Query().update(cls, **kwargs)
        return query


    @classmethod
    def delete(cls):

        query = Query().delete(cls)
        return query


    def save(self):

        query = Query().save(self).query

        cursor = self.get_cursor()
        cursor.execute(query)
        self.get_session().commit()

        last_id = cursor.lastrowid
        for name, field in self.get_fields():
            if field.primary:
                self.__setattr__(name, last_id)


