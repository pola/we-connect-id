import random
import re
import requests
import string

BASE_URL = 'https://mobileapi.apps.emea.vwapps.io'


class WeConnectId:
    def __init__(self, email_address, password):
        self._email_address = email_address
        self._password = password

        self._setup_session()
        self._sign_in()

    def _setup_session(self):
        self._session = requests.session()

        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        })

    def _sign_in(self):
        nonce = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=16))

        r = self._session.get('https://login.apps.emea.vwapps.io/authorize?nonce=' + nonce + '&redirect_uri=weconnect://authenticated')

        # Enter e-mail address
        post_data = {
            '_csrf': re.search('name="_csrf" value="([^"]+)"', r.text).group(1),
            'relayState': re.search('name="relayState" value="([^"]+)"', r.text).group(1),
            'hmac': re.search('name="hmac" value="([^"]+)"', r.text).group(1),
            'email': self._email_address,
        }

        uuid = re.search('action="/signin-service/v1/([^@]+)@apps_vw-dilab_com/login/identifier"', r.text).group(1)

        r = self._session.post(
            'https://identity.vwgroup.io/signin-service/v1/' + uuid + '@apps_vw-dilab_com/login/identifier',
            data=post_data
        )

        # Enter password
        post_data = {
            '_csrf': re.search('name="_csrf" value="([^"]+)"', r.text).group(1),
            'relayState': re.search('name="relayState" value="([^"]+)"', r.text).group(1),
            'hmac': re.search('name="hmac" value="([^"]+)"', r.text).group(1),
            'email': self._email_address,
            'password': self._password,
        }

        uuid = re.search('action="/signin-service/v1/([^@]+)@apps_vw-dilab_com/login/authenticate"', r.text).group(1)

        access_token = None

        try:
            r = self._session.post(
                'https://identity.vwgroup.io/signin-service/v1/' + uuid + '@apps_vw-dilab_com/login/authenticate',
                data=post_data
            )

        except requests.exceptions.InvalidSchema as e:
            # We expect a redirect to 'weconnect://authenticated', which requests doesn't understand
            access_token = re.search('access_token=([^&$]+)', str(e)).group(1)

        self._session.headers.update({
            'Authorization': 'Bearer ' + access_token,
        })

    def get(self, endpoint):
        return self._session.get(BASE_URL + endpoint).json()
