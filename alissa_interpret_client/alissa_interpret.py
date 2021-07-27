from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

from . import utils


class AlissaInterpret(object):
    "Alissa Interpret Public Api Client interface"

    def __init__(self, baseuri, client_id, client_secret, username, password):
        """Construct a new Alissa Interpret Public Api Client interface

        :param baseuri: Base uri for the Alissa server
        :param client_id: client id received from Agilent
        :param client_secret: client secret received from Agilent
        :param username: account name of the Alissa user account
        :param password: account password of Alissa the user account
        """
        self.baseuri = baseuri

        # Authenticate with OAuth2 and create a new session
        # ToDo: Add token caching to reuse token between sessions.
        self.session = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
        self.session.fetch_token(
            token_url=f'{self.baseuri}/auth/oauth/token',
            username=username, password=password,
            client_id=client_id, client_secret=client_secret
        )

    def _get(self, end_point, params=None, **kwargs):
        """
        Get data from the end_point, combining baseuri, api uri and end_point. Return the response as decoded json

        :param end_point: end point to get data from
        :param params: Optional params dict

        """
        uri = f'{self.baseuri}/interpret/api/2/{end_point}'
        return self.session.get(uri, params=params, **kwargs).json()

    def _post(self, end_point, data=None, json=None, **kwargs):
        """
        Post data to the end_point, combining baseuri, api uri and end_point. Return the response as decoded json

        :param end_point: end point to post data to
        :param data: Optional dictionary, list of tuples, bytes, or file-like object
        :param json: Optional json data
        """
        uri = f'{self.baseuri}/interpret/api/2/{end_point}'
        return self.session.post(uri, data, json, **kwargs).json()

    def _get_params(self, **kwargs):
        """Convert keyword arguments to a dictionary."""
        params = dict()
        for key, value in kwargs.items():
            if value is not None:
                params[utils.snake_to_camel_case(key)] = value
        return params

    def get_analyses(self, **kwargs):
        """Get all analyses. When kwargs are provided the result is limited to the analyses matching the criteria."""
        params = self._get_params(**kwargs)
        return self._get('analyses', params)

    def get_analysis(self, id):
        """
        Get an analysis via id.

        :param id: analysis id
        """
        return self._get(f'analyses/{id}')

    def get_data_files(self, **kwargs):
        """Get all data files. When kwargs are provided the result is limited to the data files matching the criteria."""
        params = self._get_params(**kwargs)
        return self._get('data_files', params)

    def get_data_file(self, id):
        """
        Get an data file via id.

        :param id: data file id
        """
        return self._get(f'data_files/{id}')

    def post_data_file(self, file, type):
        """
        Upload a new file.

        :param file: path to file
        :param type: The type of the data file. This type is used to select the correct file parser.
                     In order to use the default VCF parser the value ‘VCF_FILE’ should be provided.
        """
        files = {'file': open(file, 'r')}
        params = {'type': type}
        return self._post('data_files', files=files, params=params)