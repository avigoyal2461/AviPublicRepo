from binascii import Error
from resources.SiteCapture.SiteCaptureAPI import SiteCaptureAPI
import io
import zipfile
import os

class SiteCapture:
    def __init__(self):
        self.api = SiteCaptureAPI()

    def __repr__(self) -> str:
        return f"<SiteCapture user={self.api.USER}>"

    def search(self, query) -> list:
        """
        Searches for projects with a generic query.
        """
        res = self.api.search(query)
        if res.ok:
            return res.json()
        return []

    def recent_project_ids(self, status=None, project_type=None, count=10) -> list:
        """
        Gets the most recent project ids.
        """
        project_ids = []
        while count > 100:
            offset = count - 100
            res = self.api.get_projects(status, project_type, 100, offset)
            if res.ok:
                project_ids += [project['id'] for project in res.json()]
            count -= 100
        res = self.api.get_projects(status, project_type, count)
        if res.ok:
            project_ids += [project['id'] for project in res.json()]
        return project_ids

    def download_project_pictures(self, project_id, dst, subfolders=False) -> str:
        """
        Downloads a project's pictures to a specified directory.
        If not given, ./temp is used.
        """
        if not os.path.exists(dst):
            raise FileExistsError(f"Could not find folder {dst}")
        folder = os.path.join(dst, project_id)
        os.makedirs(folder)
        res = self.api.get_project_photos(project_id, subfolders)
        if res.ok:
            zipper = zipfile.ZipFile(io.BytesIO(res.content))
            try:
                zipper.extractall(folder)
            except FileNotFoundError:
                pass
            return folder
        return ""