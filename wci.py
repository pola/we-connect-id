import json
import random
import re
import requests
import string

#BASE_URL = 'https://mobileapi.apps.emea.vwapps.io'
BASE_URL = 'https://emea.bff.cariad.digital/vehicle/v1'
LOGIN_URL= 'https://emea.bff.cariad.digital/user-login/v1'

def generate_url():
    nonce = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=16))

    return LOGIN_URL + '/authorize?nonce=' + nonce + '&redirect_uri=weconnect://authenticated'

class WeConnectId:
    def __init__(self, email_address, password, access_token=None):
        self._email_address = email_address
        self._password = password
        self._access_token = access_token

        self._setup_session()
        self._sign_in()

    def _setup_session(self):
        self._session = requests.session()

        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        })

    def _sign_in(self, force=False):
        if self._access_token is None or force:
            r = self._session.get(generate_url())

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

            some_data = json.loads(re.search('templateModel: ({.*}),', r.text).group(1))

            # Enter password
            post_data = {
                '_csrf': re.search('csrf_token: \'([^\']+)\'', r.text).group(1),
                'relayState': some_data['relayState'],
                'hmac': some_data['hmac'],
                'email': self._email_address,
                'password': self._password,
            }

            try:
                r = self._session.post(
                    'https://identity.vwgroup.io/signin-service/v1/' + some_data['clientLegalEntityModel']['clientId'] + '/login/authenticate',
                    data=post_data
                )

                if 'Confirm Terms of Use' in r.text:
                    some_data = json.loads(re.search('templateModel: (.*),', r.text).group(1))

                    r = self._session.post('https://identity.vwgroup.io/signin-service/v1/' + some_data['clientLegalEntityModel']['clientId'] + '/terms-and-conditions',
                    data={
                        'countryOfResidence': 'SE',
                        'legalDocuments[0].name': 'dataPrivacy',
                        'legalDocuments[0].language': 'sv',
                        'legalDocuments[0].version': '2.0',
                        'legalDocuments[0].updated': 'yes',
                        'legalDocuments[0].countryCode': 'se',
                        'legalDocuments[0].skippable': 'no',
                        'legalDocuments[0].declinable': 'no',
                        '_csrf': re.search('csrf_token: \'([^\']+)\'', r.text).group(1),
                        'relayState': some_data['relayState'],
                        'hmac': some_data['hmac'],
                    })

            except requests.exceptions.InvalidSchema as e:
                # We expect a redirect to 'weconnect://authenticated', which requests doesn't understand
                self._access_token = re.search('access_token=([^&$]+)', str(e)).group(1)

        self._session.headers.update({
            'Authorization': 'Bearer ' + self._access_token,
        })

    def get_access_token(self):
        return self._access_token

    def get(self, endpoint):
        r = self._session.get(BASE_URL + endpoint)

        if r.status_code == 401:
            self._sign_in(True)

            r = self._session.get(BASE_URL + endpoint)

        return r.json()
