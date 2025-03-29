import sqlite3
from typing import Any, Dict, List, Optional
import logging

logging.basicConfig(level=logging.DEBUG)


# Abstract Model class
class Model:
    id: Optional[int] = None
    table_name: str = ""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_id(self) -> int:
        return self.id

    @classmethod
    def get_connection(cls):
        """Get a connection to the database."""
        return sqlite3.connect('clients.db')

    @classmethod
    def create_table(cls):
        """Dynamically create a table based on the class attributes."""
        fields = []
        for field, field_type in cls.__annotations__.items():
            sql_type = cls.python_type_to_sql_type(field_type)
            fields.append(f"{field} {sql_type}")
        fields_sql = ", ".join(fields)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {cls.table_name} ({fields_sql})"
        with cls.get_connection() as conn:
            conn.execute(create_table_sql)

    @staticmethod
    def python_type_to_sql_type(py_type):
        """Map Python types to SQLite types."""
        type_mapping = {
            str: "TEXT",
            int: "INTEGER",
            float: "REAL",
            bool: "INTEGER",
            list: "TEXT",
        }
        return type_mapping.get(py_type, "TEXT")

    import logging

    logging.basicConfig(level=logging.DEBUG)

    def save(self):
        """Save the current instance to the database, updating on conflict."""
        fields = list(self.__annotations__.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = [self._serialize_value(getattr(self, field)) for field in fields]

        logging.debug("Fields: %s", fields)
        logging.debug("Placeholders: %s", placeholders)
        logging.debug("Values: %s", values)

        # Prepare the ON CONFLICT clause if a unique field is specified
        if self.unique_field:
            updates = ", ".join(f"{field} = excluded.{field}" for field in fields if field != self.unique_field)
            insert_sql = f"""
            INSERT INTO {self.table_name} ({', '.join(fields)})
            VALUES ({placeholders})
            ON CONFLICT({self.unique_field}) DO UPDATE SET {updates}
            """
        else:
            insert_sql = f"INSERT OR REPLACE INTO {self.table_name} ({', '.join(fields)}) VALUES ({placeholders})"

        logging.debug("Generated SQL: %s", insert_sql)

        with self.get_connection() as conn:
            try:
                conn.execute(insert_sql, values)
                logging.debug("SQL executed successfully.")
            except Exception as e:
                logging.error("SQL execution failed: %s", e)
                raise e

        return self

    @classmethod
    def get(cls, **kwargs) -> list["Model"]:
        """Retrieve multiple model instances based on query parameters."""
        conditions = " AND ".join(f"{key} = ?" for key in kwargs.keys())
        values = list(kwargs.values())

        select_sql = f"SELECT * FROM {cls.table_name} WHERE {conditions}"

        with cls.get_connection() as conn:
            cursor = conn.execute(select_sql, values)
            rows = cursor.fetchall()
            if rows:
                field_names = [description[0] for description in cursor.description]
                # Use the current class (cls) to ensure the subclass is used for instantiation
                return [cls(**cls._deserialize_row(dict(zip(field_names, row)))) for row in rows]
        return []

    def delete(self) -> bool:
        """
        Delete the current instance from the database based on its unique identifier.
        Returns True if the deletion was successful, False otherwise.
        """
        if not hasattr(self, "id") or self.id is None:
            raise ValueError("The instance must have a valid 'id' to be deleted.")

        delete_sql = f"DELETE FROM {self.table_name} WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(delete_sql, (self.id,))
            return cursor.rowcount > 0  # True if rows were affected (deleted)

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Serialize values for storage in the database."""
        if isinstance(value, list):
            return ",".join(value)
        if isinstance(value, bool):
            return int(value)
        return value

    @classmethod
    def _deserialize_row(cls, row: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize row values back into Python types."""
        deserialized = {}
        for field, value in row.items():
            field_type = cls.__annotations__.get(field, str)
            if field_type == bool:
                deserialized[field] = bool(value)
            elif field_type == list:
                deserialized[field] = value.split(",") if value else []
            else:
                deserialized[field] = value
        return deserialized

