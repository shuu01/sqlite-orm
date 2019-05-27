import sqlite3
from field import Field

def create_session(db):

    return sqlite3.connect(db)


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

    _create_table_template = 'create table if not exists {table} ({fields} {foreign_keys})'
    _drop_table_template = 'drop table if exists {table}'
    _insert_template = 'insert into {table}({fields}) values ({values})'
    _select_template = 'select {fields} from {table} {joins}'
    _update_template = 'update {table} set {values}'
    _delete_template = 'delete from {table}'
    _join_template = 'left join {fk_table} on {fk_table}.{fk} = {pk_table}.{pk}'

    _session = None # session inside class
    __tablename__ = None

    def __init__(self, **kwargs):
        super().__init__()
        for field_name, field_instance in self.__class__.get_fields():
            self.__setattr__(field_name, kwargs.get(field_name, field_instance.default_value))

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
    def get_fields(cls):

        for name, field in cls.__dict__.items():
            if isinstance(field, Field):
                yield name, field

    @classmethod
    def get_relationships(cls):
        for name, field in cls.__dict__.items():
            if isinstance(fieid, Relationship):
                yield field

    @classmethod
    def set_relationship(cls, table, relationship):
        cls.__setattr__(table.__tablename__, relationship)

    @classmethod
    def get_fields_dict(cls):

        #return self.__dict__
        return {
            field_name: field_instance.value(getattr(cls, field_name))
            for field_name, field_instance in cls.get_fields()
        }

    @classmethod
    def get_foreign_fields(cls):

        for name, field in cls.get_fields():
            if field.foreign:
                yield field

    @classmethod
    def get_foreign_field_by_table(cls, table):

        for name, field in cls.get_fields():
            if field.foreign and field.foreign.table_class is table:
                return field


    @classmethod
    def create_table(cls):
        fields_definition = ', '.join(
            f'{name} {field.definition}' for name, field in cls.get_fields()
        )
        keys = ' '.join(
            f', {field.foreign_key_definition}' for name, field in cls.get_fields()
            if field.foreign_key_definition
        )
        query = cls._create_table_template.format(
            table = cls.__tablename__,
            fields = fields_definition,
            foreign_keys = keys,
        )
        print(query)
        cls.get_cursor().execute(query)


    @classmethod
    def drop_table(cls):
        query = cls._drop_table_template.format(
            table=cls.__tablename__
        )
        print(query)
        cls.get_cursor().execute(query)

    @classmethod
    def get(cls):

        query = cls._select_template.format(
            table = cls.__tablename__,
            fields = ', '.join(f'{cls.__tablename__}.{name}' for name, _ in cls.get_fields()),
            joins = ' '.join(cls._join_template.format(**line) for line in cls.join()),
        )
        print(query)
        result = cls.get_cursor().execute(query).fetchall()
        return result



    @classmethod
    def join(cls):

        for name, field in cls.get_fields():
            if field._fk and field.table_class == cls:
                fk_table = field._fk
                yield {
                    'fk_table': fk_table.__tablename__,
                    'fk': fk_table.get_foreign_field_by_table(cls).name,
                    'pk_table': cls.__tablename__,
                    'pk': field.name,
                }


    def save(self):

        query = self._insert_template.format(
            table = self.__tablename__,
            fields = ', '.join(self.__dict__.keys()),
            values = ', '.join(
                f'"{value}"' if value else 'NULL'
                for value in self.__dict__.values()
            ),
        )
        print(query)
        self.get_cursor().execute(query)
        self.get_session().commit()

