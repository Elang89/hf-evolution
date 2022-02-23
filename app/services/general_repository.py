from sqlite3 import DatabaseError, ProgrammingError
from typing import Any, Dict, List, Tuple
from uuid import UUID
from jinja2 import Template
from pprint import pprint

from app.sql.artifact_templates import _INSERT_TEMPLATE


class GeneralRepository(object): 

    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor()

    def insert(self, table: str, data_points: List[Dict[str, Any]]) -> None:
        params = list(data_points[0].keys())
        values = [tuple(data_point.values()) for data_point in data_points]

        sql = Template(_INSERT_TEMPLATE).render(table=table, params=params, tup_size=len(values[0]))

        self.cursor.executemany(sql, values)


        