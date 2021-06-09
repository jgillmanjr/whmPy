"""
A library for cPanel's WHM API and cPanel API (UAPI)
"""
import requests
from collections import namedtuple
from typing import Iterable, Optional

__all__ = ['Whm', 'Filter']
LATEST_WHM_API_VERSION = '1'


Filter = namedtuple('WhmFilter', ['field', 'filter_type', 'arg'])


class Whm:
    """
    The class representing a connection to the WHM API
    """

    def __init__(self, whmhost: str, username: str, token: str, whmport: str = '2087',
                 api_version: str = LATEST_WHM_API_VERSION):
        """

        :param whmhost: The WHM host to connect to
        :param username: The username to use (root or a reseller)
        :param token: The API token generated in WHM
        :param whmport: The port for WHM (secure) if non-standard
        :param api_version: The version of the WHM API to use. Defaults to the latest.
        """
        self.user = username
        self.token = token
        self.api_version = api_version
        self.output_format = 'json-api'
        self.whmhost = whmhost
        self.whmport = whmport

    def _call(self, method: str, params: Optional[dict] = None, filters: Optional[Iterable[Filter]] = None,
              columns: Optional[Iterable[str]] = None) -> dict:
        """
        Make the API call

        :param method: The API method to call
        :param params: Any parameters
        :param filters: Any filters
        :param columns: Display only these columns, or all if non specified
        :return:
        """
        if params is None:
            params = dict()
        request_headers = {'Authorization': f'whm {self.user}:{self.token}'}
        request_parameters = {'api.version': self.api_version}  # Ultimately can also include filters
        request_url = f'https://{self.whmhost}:{self.whmport}/{self.output_format}/{method}'

        for k, v in params:
            request_parameters[k] = v

        if filters is not None:
            fp = 'api.filter'
            request_parameters[f'{fp}.enable'] = 1
            current_filter_ord = ord('a')  # Start out at 'a'
            for f in filters:
                fpl = f'{fp}.{chr(current_filter_ord)}'
                request_parameters[f'{fpl}.field'] = f.field
                request_parameters[f'{fpl}.type'] = f.filter_type
                request_parameters[f'{fpl}.arg0'] = f.arg
                current_filter_ord += 1

        if columns is not None:
            cp = 'api.columns'
            request_parameters[f'{cp}.enable'] = 1
            current_column_ord = ord('a')  # Start out at 'a'
            for c in columns:
                fpl = f'{cp}.{chr(current_column_ord)}'
                request_parameters[fpl] = c
                current_column_ord += 1

        r = requests.get(url=request_url, params=request_parameters, headers=request_headers)
        print(r.url)

        return r.json()
