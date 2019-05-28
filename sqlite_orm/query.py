class Query(object):

    _create_table_template = 'create table if not exists {table} ({fields} {foreign_keys})'
    _drop_table_template = 'drop table if exists {table}'
    _insert_template = 'insert into {table}({fields}) values ({values})'
    _select_template = 'select {fields} from {table} {joins}'
    _update_template = 'update {table} set {values}'
    _delete_template = 'delete from {table}'
    _join_template = 'left join {fk_table} on {fk_table}.{fk} = {pk_table}.{pk}'

    def __init__(self):

        #super().__init__()
        self._query = ''
        self._filter_str = ''
        self._cls = None

    @property
    def query(self):

        query = self._query
        if self._filter_str:
            query += ' where {}'.format(self._filter_str)

        print(f'query: {query}')

        return query

    def create_table(self, cls):

        fields_definition = ', '.join(
            f'{name} {field.definition}' for name, field in cls.get_fields()
        )
        keys = ' '.join(
            f', {field.foreign_key_definition}' for name, field in cls.get_fields()
            if field.foreign_key_definition
        )
        self._query = self._create_table_template.format(
            table = cls.__tablename__,
            fields = fields_definition,
            foreign_keys = keys,
        )

        return self

    def drop_table(self, cls):

        self._query = self._drop_table_template.format(
            table = cls.__tablename__,
        )

        return self

    def get(self, cls, *args):

        self._cls = cls
        fk_fields = {}

        for name, field in cls.get_fields():
            if field._fk and field.table_class == cls:
                fk_table = field._fk
                fk_fields = dict(fk_table.get_fields())

        all_fields = dict(cls.get_fields())
        all_fields.update(fk_fields)

        fields = {name: field for name, field in all_fields.items() if name in args}

        if not fields:
            fields = all_fields

        self._query = self._select_template.format(
            table = cls.__tablename__,
            fields = ', '.join(f'{field.full_name}' for name, field in fields.items()),
            joins = ' '.join(self._join_template.format(**line) for line in self.join()),
        )

        return self

    def call(self):

        return self._cls.get_cursor().execute(self.query).fetchall()
        self._cls.get_session().commit()

    def update(self, cls, **kwargs):

        self._cls = cls
        fields = {
            key: cls.get_field_by_name(key).__class__.value(value)
            for key, value in kwargs.items()
        }

        self._query = self._update_template.format(
            table = cls.__tablename__,
            values = ', '.join(f'{field} = "{value}"' for field, value in fields.items())
        )

        return self

    def delete(self, cls):

        self._cls = cls
        self._query = self._delete_template.format(
            table = cls.__tablename__,
        )
        return self

    def join(self):

        cls = self._cls

        for name, field in cls.get_fields():
            if field._fk and field.table_class == cls:
                fk_table = field._fk
                yield {
                    'fk_table': fk_table.__tablename__,
                    'fk': fk_table.get_foreign_field_by_table(cls).name,
                    'pk_table': cls.__tablename__,
                    'pk': field.name,
                }

    def filter(self, condition):

        self._filter_str = str(condition)
        return self

    def save(self, cls):

        self._query = self._insert_template.format(
            table = cls.__tablename__,
            fields = ', '.join(cls.__dict__.keys()),
            values = ', '.join(
                f'"{value}"' if value else 'NULL'
                for value in cls.__dict__.values()
            ),
        )

        return self
