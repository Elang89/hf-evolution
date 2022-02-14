from sqlite3 import DatabaseError
from typing import Any, Dict, List, Tuple
from jinja2 import Template
from pprint import pprint

from app.sql.artifact_templates import _INSERT_TEMPLATE, _VERIFY_TEMPLATE


class GeneralRepository(object): 

    def __init__(self, conn):
        self.conn = conn


    def verify(self, table: str, field: str, value: str) -> bool: 
        sql = Template(_VERIFY_TEMPLATE).render(table=table, field=field, value=value)
        cursor = self.conn.cursor()
        cursor.execute(sql)

        result = cursor.fetchone()[0]

        return bool(result)

    def insert(self, table: str, data_points: List[Dict[str, Any]]) -> None:
        params = list(data_points[0].keys())
        values = [tuple(data_point.values()) for data_point in data_points]

        sql = Template(_INSERT_TEMPLATE).render(table=table, params=params, tup_size=len(values[0]))

        try:
            cursor = self.conn.cursor()
            cursor.executemany(sql, values)
            self.conn.commit()
        except DatabaseError as error:
            pprint(error)
            self.conn.rollback()

        