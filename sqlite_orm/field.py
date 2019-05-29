class MetaType(type):

    def __str__(self):
        return self.__name__


class Integer(metaclass=MetaType):
    ''' Integer field type '''

    pass


class String(metaclass=MetaType):
    ''' String field type '''

    def __init__(self, length=100):
        self.length = length

    def __str__(self):
        return f'Varchar({self.length})'


class Field(object):

    _template_definition = '{type} {not_null} {primary_key} {autoincrement}'
    _template_foreign_definition = 'foreign key ({self_name}) references {table}({field})'
    _template_cmp = '{field_name} {operator} {other}'

    def __init__(self,
        type=None, # field type
        primary=False, # primary key
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
        ''' used for create table '''
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
        ''' used for create table with foreign key '''
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


    @property
    def full_name(self):
        return '{}.{}'.format(self.tablename, self.name)


    def _fill_template_cmp(self, field_name, operator, other):
        ''' used for filter operator '''
        return self._template_cmp.format(
            field_name=field_name,
            operator=operator,
            other=repr(other),
        )


    def __repr__(self):
        return self.full_name


    def __eq__(self, other):
        return self._fill_template_cmp(self, '=', other)
