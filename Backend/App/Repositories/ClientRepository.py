from typing import List, Optional
from OnSiteServerApplication.Backend.App.Models.ClientModel import ClientModel


class ClientRepository:
    """Repository class for managing ClientModel interactions with the database."""

    @staticmethod
    def add_client(client: ClientModel) -> None:
        """Add a new client to the database."""
        client.save()

    @staticmethod
    def get_client_by_uuid(uuid: str) -> Optional[List[ClientModel]]:
        """Retrieve a client by MAC address."""
        return ClientModel.get(uuid=uuid)

    @staticmethod
    def get_client_by_mac_address(mac_address: str) -> Optional[List[ClientModel]]:
        """Retrieve a client by MAC address."""
        return ClientModel.get(mac_address=mac_address)

    @staticmethod
    def get_client_by_nickname(nickname: str) -> Optional[ClientModel]:
        """Retrieve a client by nickname."""
        return ClientModel.get(nickname=nickname)

    @staticmethod
    def get_all_clients() -> List[ClientModel]:
        """Retrieve all clients from the database."""
        with ClientModel.get_connection() as conn:
            cursor = conn.execute(f"SELECT * FROM {ClientModel.table_name}")
            rows = cursor.fetchall()
            field_names = [description[0] for description in cursor.description]
            return [ClientModel(**ClientModel._deserialize_row(dict(zip(field_names, row)))) for row in rows]

    @staticmethod
    def update_client(client: ClientModel) -> None:
        """Update an existing client in the database."""
        client.save()

    @staticmethod
    def delete_client_by_mac_address(mac_address: str) -> None:
        """Delete a client by MAC address."""
        with ClientModel.get_connection() as conn:
            conn.execute(f"DELETE FROM {ClientModel.table_name} WHERE mac_address = ?", (mac_address,))

    @staticmethod
    def get_clients_with_shutdown_status(shutdown: bool) -> List[ClientModel]:
        """Retrieve clients by their shutdown status."""
        with ClientModel.get_connection() as conn:
            cursor = conn.execute(
                f"SELECT * FROM {ClientModel.table_name} WHERE shutdown = ?", (int(shutdown),)
            )
            rows = cursor.fetchall()
            field_names = [description[0] for description in cursor.description]
            return [ClientModel(**ClientModel._deserialize_row(dict(zip(field_names, row)))) for row in rows]
