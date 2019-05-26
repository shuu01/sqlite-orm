

import sqlite3

def create_session(db):

    return sqlite3.connect(db)


class MetaType(type):
    
    def __str__(self):
        return self.__name__

class Integer(metaclass=MetaType):

    pass        

class String(metaclass=MetaType):

    def __init__(self, length=100):
        self.length = length

    def __str__(self):
        return f'Varchar({self.length})'


class Field(object):

    _template_definition = '{type} {not_null} {primary_key} {autoincrement}'
    _template_foreign_definition = 'FOREIGN KEY ({self_name}) references {table}({field})'

    def __init__(self,
        type=None,
        primary=False,
        autoincrement=False,
        not_null=True,
        foreign=None,
    ):
        if not type:
            raise Exception('Please, specify type of column')
        else:
            self.type = type
        
        self.primary = primary
        self.autoincrement = autoincrement
        self.not_null = not_null
        self.foreign = foreign
        self.table_class = None

    @property
    def definition(self):
        return self._template_definition.format(**self._definition_dict)

    @property
    def _definition_dict(self):
        return {
            'type': self.type,
            'not_null': 'NOT NULL' if self.not_null else '',
            'primary_key': 'PRIMARY KEY' if self.primary else '',
            'autoincrement': 'AUTOINCREMENT' if self.autoincrement else '',
        }

    @property
    def foreign_key_definition(self):
        if self.foreign:
            return self._template_foreign_definition.format(
                self_name=self.name,
                table=self.foreign.tablename,
                field=self.foreign.name
            )

    @property
    def name(self):
        return self.table_class.get_field_name(self)

    @property
    def tablename(self):
        return self.table_class.__tablename__

    def set_table_class(self, cls):
        self.table_class = cls


class MetaBase(type):
    # metaclass magic, that set table class attribute for every field in this class
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, Field):
                attr_value.set_table_class(cls)

class Base(metaclass=MetaBase):

    _create_table_template = 'create table if not exists {table} ({fields} {foreign_keys})'
    _drop_table_template = 'drop table if exists {table}'
    _insert_template = 'insert into {table}({fields}) values ({values})'
    _select_template = 'select {fields} from {table}'
    _update_template = 'update {table} set {values}'
    _delete_template = 'delete from {table}'
    
    _session = None # session inside class
    __tablename__ = None

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
    def create_table(cls):
        fields_definition = ', '.join(
            f'{name} {field.definition}' for name, field in cls.get_fields()
        )
        keys = ' '.join(
            f', {field.foreign_key_definition}' for _, field in cls.get_fields()
            if field.foreign_key_definition
        )
        query = cls._create_table_template.format(
            table = cls.__tablename__,
            fields = fields_definition,
            foreign_keys = keys,
        )
        print(query)
        cls.get_cursor().execute(query)
 
