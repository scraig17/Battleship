import logging
from typing import Any, Optional
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth

from .errors import AuthenticationRequiredError

logger = logging.getLogger(__name__)


class UsersApiClient:
    """
    A client for the Users API.
    """

    USERS_PATH = "/users"

    def __init__(self, base_url):
        """
        Creates a new instance.
        :param base_url: base URL for the API server
        """
        self.base_url = base_url
        self._auth = None

    def _href_for_uid(self, uid: str, suffix: str = None):
        href = f"{self.USERS_PATH}/{uid}"
        if suffix:
            href = f"{href}/{suffix}"
        return href

    def auth(self, uid: str, password: str):
        """
        Sets the authentication details for the API methods that require authentication
        :param uid: user ID
        :param password: password
        """
        self._auth = HTTPBasicAuth(uid, password)

    def create_user(self, uid: str, password: str, nickname: str = None, full_name: str = None, custom: Any = None) -> tuple[dict, str]:
        """
        Creates a new user.
        :param uid: user ID
        :param password: password
        :param nickname: (optional) nickname
        :param full_name: (optional) full name
        :param custom: (optional) custom data which may be any simple type (str, number, boolean) or dict or list
            containing any of these types -- i.e. anything that can be represented in JSON
        :return: dict containing the details of the created user
        """
        url = urljoin(self.base_url, self.USERS_PATH)
        data = {
            "uid": uid,
            "password": password,
        }
        if full_name:
            data["full_name"] = full_name
        if nickname:
            data["nickname"] = nickname
        if custom:
            data["custom"] = custom

        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json(), response.headers.get("ETag")

    def fetch_user(self, uid_or_href: str) -> Optional[dict]:
        """
        Fetches a user.
        :param uid_or_href: either the user ID or an href for the user to be fetched
        :return: dict containing the details of the user or None if the user was not found
        """
        if not uid_or_href.startswith("/"):
            url = urljoin(self.base_url, self._href_for_uid(uid_or_href))
        else:
            url = urljoin(self.base_url, uid_or_href)

        response = requests.get(url)

        # if the user wasn't found return None instead of raising an error
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json(), response.headers.get("ETag")

    def delete_user(self, uid_or_href: str):
        """
        Deletes a user.
        :param uid_or_href: either the user ID or an href for the user to be deleted
        :return:
        """
        if not self._auth:
            raise AuthenticationRequiredError()
        if not uid_or_href.startswith("/"):
            url = urljoin(self.base_url, self._href_for_uid(uid_or_href))
        else:
            url = urljoin(self.base_url, uid_or_href)
        response = requests.delete(url, auth=self._auth)
        response.raise_for_status()

    def update_user(self, uid_or_href, data, etag):
        """
        Updates a user.
        :param uid_or_href: either the user ID or an href for the user to be updated
        :param data: dict as returned by fetch_user with properties updated as desired
        :return: dict containing the updated user details
        """
        if not self._auth:
            raise AuthenticationRequiredError()
        if not uid_or_href.startswith("/"):
            url = urljoin(self.base_url, self._href_for_uid(uid_or_href))
        else:
            url = urljoin(self.base_url, uid_or_href)
        response = requests.put(url, json=data, headers={"If-Match": etag}, auth=self._auth)
        response.raise_for_status()
        return response.json(), response.headers.get("ETag")

    def change_password(self, uid_or_href: str, password: str):
        """
        Change a user's password.
        :param uid_or_href: either the user ID or an href for the user whose password is to be changed
        :param password: the new password
        :return:
        """
        if not self._auth:
            raise AuthenticationRequiredError()
        if not uid_or_href.startswith("/"):
            url = urljoin(self.base_url, self._href_for_uid(uid_or_href, "password`"))
        else:
            url = urljoin(self.base_url, uid_or_href)

        response = requests.put(url, data=password, auth=self._auth)
        response.raise_for_status()
