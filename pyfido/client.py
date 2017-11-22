"""
Pyfido
"""
import asyncio
import json
import logging
import re

import aiohttp


REQUESTS_TIMEOUT = 15

JANRAIN_CLIENT_ID = "bfkecrvys7sprse8kc4wtwugr2bj9hmp"
HOST_JANRAIN = "https://rogers-fido.janraincapture.com"
HOST_FIDO = "https://www.fido.ca/pages/api/selfserve"
LOGIN_URL = "{}/widget/traditional_signin.jsonp".format(HOST_JANRAIN)
TOKEN_URL = "{}/widget/get_result.jsonp".format(HOST_JANRAIN)
ACCOUNT_URL = "{}/v3/login".format(HOST_FIDO)
LIST_NUMBERS_URL = "{}/v2/accountOverview".format(HOST_FIDO)
BALANCE_URL = "{}/v2/accountOverview".format(HOST_FIDO)
FIDO_DOLLAR_URL = "{}/v1/wireless/rewards/basicinfo".format(HOST_FIDO)
USAGE_URL = "{}/v1/postpaid/dashboard/usage".format(HOST_FIDO)

DATA_MAP = {'data': ('data', 'D'),
            'text': ('text', 'BL'),
            'mms': ('text', 'M'),
            'text_int': ('text', 'SI'),
            'talk': ('talk', 'V'),
            'other_talk': ('talk', 'VL')}


class PyFidoError(Exception):
    pass


class FidoClient(object):

    def __init__(self, username, password, timeout=REQUESTS_TIMEOUT):
        """Initialize the client object."""
        self.username = username
        self.password = password
        self._phone_numbers = []
        self._timeout = timeout
        self._data = {}
        self._headers = {'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64; '
                                       'rv:10.0.7) Gecko/20100101 '
                                       'Firefox/10.0.7 Iceweasel/10.0.7')}
        self._session = None

    @asyncio.coroutine
    def _post_login_page(self):
        """Login to Janrain."""
        # Prepare post data
        data = {
            "form": "signInForm",
            "client_id": JANRAIN_CLIENT_ID,
            "redirect_uri": "https://www.fido.ca/pages/#/",
            "response_type": "token",
            "locale": "en-US",
            "userID": self.username,
            "currentPassword": self.password,
        }
        # HTTP request
        try:
            raw_res = yield from self._session.post(LOGIN_URL,
                                                    headers=self._headers,
                                                    data=data,
                                                    timeout=self._timeout)
        except OSError:
            raise PyFidoError("Can not sign in")

        return True

    @asyncio.coroutine
    def _get_token(self):
        """Get token from JanRain."""
        # HTTP request
        try:
            raw_res = yield from self._session.get(TOKEN_URL,
                                                   headers=self._headers,
                                                   timeout=self._timeout)
        except OSError:
            raise PyFidoError("Can not get token")
        # Research for json in answer
        content = yield from raw_res.text()
        reg_res = re.search(r"\({.*}\)", content)
        if reg_res is None:
            raise PyFidoError("Can not finf token json")
        # Load data as json
        return_data = json.loads(reg_res.group()[1:-1])
        # Get token and uuid
        token = return_data.get('result', {}).get('accessToken')
        uuid = return_data.get('result', {}).get('userData', {}).get('uuid')
        # Check values
        if token is None or uuid is None:
            raise PyFidoError("Can not get token or uuid")

        return token, uuid

    @asyncio.coroutine
    def _get_account_number(self, token, uuid):
        """Get fido account number."""
        # Data
        data = {"accessToken": token,
                "uuid": uuid}
        # Http request
        try:
            raw_res = yield from self._session.post(ACCOUNT_URL,
                                                    data=data,
                                                    headers=self._headers,
                                                    timeout=self._timeout)
        except OSError:
            raise PyFidoError("Can not get account number")
        # Load answer as json
        try:
            json_content = yield from raw_res.json()
            account_number = json_content\
                            .get('getCustomerAccounts', {})\
                            .get('accounts', [{}])[0]\
                            .get('accountNumber')
        except (OSError, ValueError):
            raise PyFidoError("Bad json getting account number")
        # Check collected data
        if account_number is None:
            raise PyFidoError("Can not get account number")

        return account_number

    @asyncio.coroutine
    def _list_phone_numbers(self, account_number=None):
        # Data
        data = {"accountNumber": account_number,
                # Language setting is useless
                # "language": "fr",
                "refresh": False}
        # Http request
        try:

            raw_res = yield from self._session.post(LIST_NUMBERS_URL,
                                                    data=data,
                                                    headers=self._headers,
                                                    timeout=self._timeout)
        except OSError:
            raise PyFidoError("Can not get account number")
        # Load answer as json
        phone_number_list = []
        try:
            # Get phone numbers
            json_content = yield from raw_res.json()
            services = json_content.get('getAccountInfo', {})\
                .get('subscriberService', [])
            for service in services:
                number = service.get('service', [{}])[0].get('subscriberNo')
                phone_number_list.append(number)
        except (OSError, ValueError):
            raise PyFidoError("Bad json getting account number")
        # Check collected data
        if phone_number_list == []:
            raise PyFidoError("Can not get phone numbers")

        return phone_number_list

    @asyncio.coroutine
    def _get_balance(self, account_number):
        """Get current balance from Fido."""
        # Prepare data
        data = {"ctn": self.username,
                "language": "en-US",
                "accountNumber": account_number}
        # Http request
        try:
            raw_res = yield from self._session.post(BALANCE_URL,
                                                    data=data,
                                                    headers=self._headers,
                                                    timeout=self._timeout)
        except OSError:
            raise PyFidoError("Can not get balance")
        # Get balance
        try:
            json_content = yield from raw_res.json()
            balance_str = json_content\
                            .get("getAccountInfo", {})\
                            .get("balance")
        except (OSError, ValueError):
            raise PyFidoError("Can not get balance as json")
        if balance_str is None:
            raise PyFidoError("Can not get balance")
        # Casting to float
        try:
            balance = float(balance_str)
        except ValueError:
            raise PyFidoError("Can not get balance as float")

        return balance

    @asyncio.coroutine
    def _get_fido_dollar(self, account_number, number):
        """Get current Fido dollar balance."""
        # Prepare data
        data = json.dumps({"fidoDollarBalanceFormList":
                           [{"phoneNumber": number,
                             "accountNumber": account_number}]})
        # Prepare headers
        headers_json = self._headers.copy()
        headers_json["Content-Type"] = "application/json;charset=UTF-8"
        # Http request
        try:
            raw_res = yield from self._session.post(FIDO_DOLLAR_URL,
                                                    data=data,
                                                    headers=headers_json,
                                                    timeout=self._timeout)
        except OSError:
            raise PyFidoError("Can not get fido dollar")
        # Get fido dollar
        try:
            json_content = yield from raw_res.json()
            fido_dollar_str = json_content\
                        .get("fidoDollarBalanceInfoList", [{}])[0]\
                        .get("fidoDollarBalance")
        except (OSError, ValueError):
            raise PyFidoError("Can not get fido dollar as json")
        if fido_dollar_str is None:
            raise PyFidoError("Can not get fido dollar")
        # Casting to float
        try:
            fido_dollar = float(fido_dollar_str)
        except ValueError:
            raise PyFidoError("Can not get fido dollar")

        return fido_dollar

    @asyncio.coroutine
    def _get_usage(self, account_number, number):
        """Get Fido usage.

        Get the following data
        - talk
        - text
        - data

        Roaming data is not supported yet
        """
        # Prepare data
        data = {"ctn": number,
                "language": "en-US",
                "accountNumber": account_number}
        # Http request
        try:
            raw_res = yield from self._session.post(USAGE_URL,
                                                    data=data,
                                                    headers=self._headers,
                                                    timeout=self._timeout)
        except OSError:
            raise PyFidoError("Can not get usage")
        # Load answer as json
        try:
            output = yield from raw_res.json()
        except (OSError, ValueError):
            raise PyFidoError("Can not get usage as json")
        # Format data
        ret_data = {}
        for data_name, keys in DATA_MAP.items():
            key, subkey = keys
            for data in output.get(key)[0].get('wirelessUsageSummaryInfoList'):
                if data.get('usageSummaryType') == subkey:
                    # Prepare keys:
                    used_key = "{}_used".format(data_name)
                    remaining_key = "{}_remaining".format(data_name)
                    limit_key = "{}_limit".format(data_name)
                    # Get values
                    ret_data[used_key] = data.get('used', 0.0)
                    if data.get('remaining') >= 0:
                        ret_data[remaining_key] = data.get('remaining')
                    else:
                        ret_data[remaining_key] = None
                    if data.get('total') >= 0:
                        ret_data[limit_key] = data.get('total')
                    else:
                        ret_data[limit_key] = None

        return ret_data

    @asyncio.coroutine
    def fetch_data(self):
        """Fetch the latest data from Fido."""
        with aiohttp.ClientSession() as session:
            self._session = session
            # Post login page
            yield from self._post_login_page()
            # Get token
            token_uuid = yield from self._get_token()
            # Get account number
            account_number = yield from self._get_account_number(*token_uuid)
            # List phone numbers
            self._phone_numbers = yield from self._list_phone_numbers(account_number)
            # Get balance
            balance = yield from self._get_balance(account_number)
            self._data['balance'] = balance
            # Get fido dollar
            for number in self._phone_numbers:
                fido_dollar = yield from self._get_fido_dollar(account_number,
                                                               number)
                self._data[number]= {'fido_dollar': fido_dollar}
            # Get usage
            for number in self._phone_numbers:
                usage = yield from self._get_usage(account_number, number)
                self._data[number].update(usage)

    def get_data(self):
        """Return collected data"""
        return self._data

    def get_phone_numbers(self):
        """Return list of phone numbers"""
        return self._phone_numbers
