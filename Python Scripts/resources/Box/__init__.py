from .BoxAPI import BoxAPI

class Box:
    """
    A Box integration for controlling files and folders.
    """
    def __init__(self) -> None:
        self.api = BoxAPI()
    
    def rename_file(self, file_id, new_name) -> bool:
        """
        Renames a given file id.
        """
        res = self.api.request_rename_file(file_id, new_name)
        if res.ok:
            return True
        else:
            return False