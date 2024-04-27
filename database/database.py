import sqlite3

class Database:
    def __init__(self, db_name:str):
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)

    async def join_role_status(self, server_id:int, status:bool):
        cursor = self.connection.cursor()
        cursor.execute(f"UPDATE status SET JOIN_ROLE = {status} WHERE server_id = {server_id}")
        self.connection.commit()
