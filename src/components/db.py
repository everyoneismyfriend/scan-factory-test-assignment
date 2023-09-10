import sqlite3
from contextlib import closing
from functools import partial
from typing import Iterator, Iterable

from .models import Domain, Rule


class SQLiteService:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def retrieve_domains(self, batch_size: int = 100) -> Iterator[Domain]:
        query = 'SELECT project_id, name FROM domains ORDER BY project_id'
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query)
            for batch in iter(partial(cursor.fetchmany, batch_size), []):
                for project_id, name in batch:
                    yield Domain(project_id, name)

    def create_rules(self, rules: Iterable[Rule]) -> None:
        query = 'INSERT INTO rules (project_id, regexp) VALUES (?, ?)'
        values = [(rule.project_id, rule.regexp) for rule in rules]
        with closing(self.connection.cursor()) as cursor:
            cursor.executemany(query, values)
            self.connection.commit()
