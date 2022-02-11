from typing import List, Tuple
from jinja2 import Template
from pprint import pprint

from app.sql.dataset_templates import _INSERT_TEMPLATE 

class DatasetRepository(object): 

    def __init__(self, conn):
        self.conn = conn


    def insert(self, table: str, params: List[str], values: List[Tuple]) -> None:

        sql = Template(_INSERT_TEMPLATE).render(table=table, params=params, values=values)
        pprint(sql)


        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()
        
