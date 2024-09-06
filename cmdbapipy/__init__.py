import requests
from functools import partial
from typing import Optional, Any
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

class CMDBApiException(Exception):
    pass


class CMDBApi:

    def __init__(
        self,
        username: str,
        password: str,
        timeout: Optional[int] = 30,
        debug: bool = False,
        base_url: str

    ):
        self.username = username
        self.password = password
        self.timeout = timeout
        self.base_url = base_url
        self.session = requests.Session()
        self.session_id = None
        self.debug = debug
        if self.debug:
            # Enable HTTP request & response logging
            self.session.hooks['response'] = [self.log_response]

    @staticmethod
    def pretty_print_json(data):
        try:
            return json.dumps(json.loads(data), indent=2)
        except json.JSONDecodeError:
            # Data is not JSON, just return it as is
            return data


    def log_response(self, r, *args, **kwargs):
        # Log the outgoing request details
        logger.debug(f"Request: {r.request.method} {r.request.url} {r.status_code}")
        if r.request.body:
            logger.debug(f"Request Body: {self.pretty_print_json(r.request.body)}")
        logger.debug(f"Request Headers: {json.dumps(dict(r.request.headers), indent=2)}")

        # Log the incoming response details
        logger.debug(f"Response Body: {self.pretty_print_json(r.text)}")
        logger.debug(f"Response Headers: {json.dumps(dict(r.headers), indent=2)}")


    def get_session_id(self):
        headers = {"content-type": "application/json"}

        data = {
            "username": self.username,
            "password": self.password,
            "role": "",
            "scope": "service"
        }

        response = self.session.post(self.base_url + "sessions?returnId=true", headers=headers, json=data, timeout=self.timeout)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code.
        self.session_id = response.json()['data']['_id']

    def handle_api_error(self, response, exception):
        self.log_response(response)
        if response.status_code != 200:
                raise exception


    def lookup_types(self, name):
        lookup_value = 'HEX' + ''.join(format(ord(char), 'x') for char in name)
        values = self.get(f"lookup_types/{lookup_value}/values/")
        mapped = {x['description']: x['_id'] for x in values['data']}
        return mapped



    def api_request(
        self,
        endpoint: str,
        method: str = "get",
        timeout: Optional[int] = None,
        params: Optional[dict] = None,
        **kwargs,
    ) -> Any:

        if self.session_id is None:
            self.get_session_id()

        url = self.base_url + endpoint
        headers = {
            "Cmdbuild-authorization": self.session_id,
            "Content-Type": "application/json",
        }
        response = self.session.request(
            method, url, headers=headers, json=kwargs.get('json',None), params=params, timeout=timeout or self.timeout
        )
        try:
            response.raise_for_status()  # Raise an HTTPError if the response is an error status
        except requests.HTTPError as e:
            logging.exception(response.text)
            self.handle_api_error(response, e)  # Handle specific API errors

        data = response.json()
        if not data['success']:
            raise CMDBApiException("CMDAPI error")
        return data

    def __getattr__(self, attr):
        return partial(self.api_request, method=attr)

