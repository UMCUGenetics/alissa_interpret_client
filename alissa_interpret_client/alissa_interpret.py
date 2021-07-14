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

    def _get(self, end_point, params=dict()):
        """
        Get data from the end_point, combining baseuri, api uri and end_point. Return the response as decoded json

        :param end_point: end point to get data from
        :param params: Optional params dict

        """
        uri = f'{self.baseuri}/interpret/api/2/{end_point}'
        return self.session.get(uri, params=params).json()

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
