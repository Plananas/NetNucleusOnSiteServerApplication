from typing import List

from App.Backend.Models.ProgramModel import ProgramModel


class ProgramRepository:
    """Repository class for managing ProgramModel interactions with the database."""

    @staticmethod
    def add_program(program: ProgramModel) -> None:
        """Add a new Program to the database."""
        program.save()

    @staticmethod
    def get_program_by_client_uuid(client_uuid: str) -> List[ProgramModel]:
        """Retrieve a program by client id."""
        print(client_uuid)

        return ProgramModel.get(client_uuid=client_uuid)


    @staticmethod
    def get_program_by_client_uuid_and_name(client_uuid: str, name: str,) -> List[ProgramModel]:
        """Retrieve a program by client id."""

        return ProgramModel.get(client_uuid=client_uuid, name=name)