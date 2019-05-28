import sqlite3

def create_session(db):

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    session = sqlite3.connect(db)
    session.row_factory = dict_factory
    return session
