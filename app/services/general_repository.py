from re import S
from typing import Any, Dict, List, Tuple
from jinja2 import Template
from pprint import pprint
from pydantic import BaseModel

from app.sql.artifact_templates import _INSERT_TEMPLATE, _VERIFY_TEMPLATE


class GeneralRepository(object): 

    def __init__(self, conn):
        self.conn = conn


    def verify(self, table: str, id: str) -> bool: 
        sql = Template(_VERIFY_TEMPLATE).render(table=table, id=id)
        cursor = self.conn.cursor()
        cursor.execute(sql)

        result = cursor.fetchone()[0]

        return (result == 1)



    def insert(self, table: str, data_points: List[Dict[str, Any]]) -> None:
        params = list(data_points[0].keys())
        values = self._convert_to_sql(data_points)

        import pdb

        pdb.set_trace()

        sql = Template(_INSERT_TEMPLATE).render(table=table, params=params, values=values)

        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        
    def _convert_to_sql(self, data_points: List[Dict[str, Any]]) -> List[Tuple]:
        values = []

        for data_point in data_points:
            tup_values = tuple(data_point.values())
            sql_values = str(tup_values)

            if len(tup_values) == 1: 
                sql_values = sql_values[:-2] + sql_values[-1]
            values.append(sql_values)

        return values
