"""
A library for cPanel's WHM API and cPanel API (UAPI)
"""
import requests
from collections import namedtuple
from typing import Iterable, Optional
from .exceptions import SortedFieldNotDisplayed

__all__ = ['Whm', 'FieldFilter', 'FieldSort']
LATEST_WHM_API_VERSION = '1'


FieldFilter = namedtuple('ColFilter', ['field', 'filter_type', 'arg'])
FieldSort = namedtuple('ColSort', ['field', 'method', 'reverse'], defaults=['lexicographic', 0])


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

    def _call(self, method: str, params: Optional[dict] = None, filters: Optional[Iterable[FieldFilter]] = None,
              fields: Optional[Iterable[str]] = None, fieldsorts: Optional[Iterable[FieldSort]] = None) -> dict:
        """
        Make the API call

        :param method: The API method to call
        :param params: Any parameters
        :param filters: Any filters
        :param fields: Display only these fields, or all if non specified
        :param fieldsorts: Columns to sort on. Order of columns applies
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
            mp = 'api.filter'
            request_parameters[f'{mp}.enable'] = 1
            current_filter_ord = ord('a')  # Start out at 'a'
            for f in filters:
                mpl = f'{mp}.{chr(current_filter_ord)}'
                request_parameters[f'{mpl}.field'] = f.field
                request_parameters[f'{mpl}.type'] = f.filter_type
                request_parameters[f'{mpl}.arg0'] = f.arg
                current_filter_ord += 1

        if fields is not None:
            mp = 'api.columns'
            request_parameters[f'{mp}.enable'] = 1
            current_column_ord = ord('a')  # Start out at 'a'
            for c in fields:
                mpl = f'{mp}.{chr(current_column_ord)}'
                request_parameters[mpl] = c
                current_column_ord += 1

        if fieldsorts is not None:
            mp = 'api.sort'
            request_parameters[f'{mp}.enable'] = 1
            current_filter_ord = ord('a')  # Start out at 'a'
            for cs in fieldsorts:
                if fields is not None and cs.field not in fields:
                    m = f''
                    raise SortedFieldNotDisplayed(f'Filed {cs.field} is specified in the sort, but not displayed')
                mpl = f'{mp}.{chr(current_filter_ord)}'
                request_parameters[f'{mpl}.field'] = cs.field
                request_parameters[f'{mpl}.method'] = cs.method
                request_parameters[f'{mpl}.reverse'] = cs.reverse
                current_filter_ord += 1

        r = requests.get(url=request_url, params=request_parameters, headers=request_headers)
        print(r.url)

        return r.json()
