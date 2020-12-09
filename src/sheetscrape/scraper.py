import gspread
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetScraper:
    """
    Wraps the functionality of gspread.
    Handles authentication and access modes.
    """

    def __init__(self, keyfile, mode="r"):
        self._keyfile = keyfile
        self._scope = self.get_scope(mode)
        self._creds = ServiceAccountCredentials.from_json_keyfile_name(
            self._keyfile, self._scope
        )
        self.client = gspread.authorize(self._creds)

    @staticmethod
    def get_scope(mode):
        result = None
        scopes = {
            "r": "https://www.googleapis.com/auth/drive.readonly",
            "rw": "https://www.googleapis.com/auth/drive",
        }
        try:
            result = [scopes[mode]]
        except KeyError:
            raise ValueError(f'Invalid access mode: {mode}. Must be either "r" or "rw"')
        return result
