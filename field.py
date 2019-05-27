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

class Relationship(object):

    def __init__(self, table):
        self.table = table

class Field(object):

    _template_definition = '{type} {not_null} {primary_key} {autoincrement}'
    _template_foreign_definition = 'foreign key ({self_name}) references {table}({field})'

    def __init__(self,
        type=None,
        primary=False,
        autoincrement=False,
        not_null=False,
        foreign=None,
        default_value=None,
    ):
        if not type:
            raise Exception('Please, specify type of column')
        else:
            self.type = type

        self.primary = primary
        self.autoincrement = autoincrement
        self.not_null = primary or not_null
        self.foreign = foreign
        self.default_value = default_value
        self.table_class = None
        self._fk = None

    @classmethod
    def value(cls, val):
        return val or 'NULL'

    @property
    def definition(self):
        return self._template_definition.format(**self._definition_dict)

    @property
    def _definition_dict(self):
        return {
            'type': self.type,
            'not_null': 'not null' if self.not_null else '',
            'primary_key': 'primary key' if self.primary else '',
            'autoincrement': 'autoincrement' if self.autoincrement else '',
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
