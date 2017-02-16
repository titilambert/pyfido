"""
Pyfido
"""
import json
import logging
import re

import requests


REQUESTS_TIMEOUT = 15

JANRAIN_CLIENT_ID = "bfkecrvys7sprse8kc4wtwugr2bj9hmp"
HOST_JANRAIN = "https://rogers-fido.janraincapture.com"
HOST_FIDO = "https://www.fido.ca/pages/api/selfserve"
LOGIN_URL = "{}/widget/traditional_signin.jsonp".format(HOST_JANRAIN)
TOKEN_URL = "{}/widget/get_result.jsonp".format(HOST_JANRAIN)
ACCOUNT_URL = "{}/v3/login".format(HOST_FIDO)
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

    def __init__(self, number, password, timeout=REQUESTS_TIMEOUT):
        """Initialize the client object."""
        self.number = number
        self.password = password
        self._timeout = timeout
        self._data = {}
        self._headers = {'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64; '
                                       'rv:10.0.7) Gecko/20100101 '
                                       'Firefox/10.0.7 Iceweasel/10.0.7')}
        self._cookies = None

    def _post_login_page(self):
        """Login to Janrain."""
        # Prepare post data
        data = {
            "form": "signInForm",
            "client_id": JANRAIN_CLIENT_ID,
            "redirect_uri": "https://www.fido.ca/pages/#/",
            "response_type": "token",
            "locale": "en-US",
            "userID": self.number,
            "currentPassword": self.password,
        }
        # HTTP request
        try:
            raw_res = requests.post(LOGIN_URL, headers=self._headers,
                                    data=data, timeout=self._timeout)
        except OSError:
            raise PyFidoError("Can not sign in")
        # Get cookies
        self._cookies = raw_res.cookies

        return True

    def _get_token(self):
        """Get token from JanRain."""
        # HTTP request
        try:
            raw_res = requests.get(TOKEN_URL,
                                   headers=self._headers,
                                   cookies=self._cookies,
                                   timeout=self._timeout)
        except OSError:
            raise PyFidoError("Can not get token")
        # Research for json in answer
        reg_res = re.search(r"\({.*}\)", raw_res.text)
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
        # Update cookies
        self._cookies.update(raw_res.cookies)

        return token, uuid

    def _get_account_number(self, token, uuid):
        """Get fido account number."""
        # Data
        data = {"accessToken": token,
                "uuid": uuid}
        # Http request
        try:
            raw_res = requests.post(ACCOUNT_URL,
                                    data=data,
                                    headers=self._headers,
                                    timeout=self._timeout)
        except OSError:
            raise PyFidoError("Can not get account number")
        # Load answer as json
        try:
            account_number = raw_res.json()\
                            .get('getCustomerAccounts', {})\
                            .get('accounts', [{}])[0]\
                            .get('accountNumber')
        except (OSError, ValueError):
            raise PyFidoError("Bad json getting account number")
        # Check collected data
        if account_number is None:
            raise PyFidoError("Can not get account number")
        # Update cookies
        self._cookies.update(raw_res.cookies)

        return account_number

    def _get_balance(self, account_number):
        """Get current balance from Fido."""
        # Prepare data
        data = {"ctn": self.number,
                "language": "en-US",
                "accountNumber": account_number}
        # Http request
        try:
            raw_res = requests.post(BALANCE_URL,
                                    data=data,
                                    headers=self._headers,
                                    cookies=self._cookies,
                                    timeout=self._timeout)
        except OSError:
            raise PyFidoError("Can not get balance")
        # Get balance
        try:
            balance_str = raw_res.json()\
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

    def _get_fido_dollar(self, account_number):
        """Get current Fido dollar balance."""
        # Prepare data
        data = json.dumps({"fidoDollarBalanceFormList":
                           [{"phoneNumber": self.number,
                             "accountNumber": account_number}]})
        # Prepare headers
        headers_json = self._headers.copy()
        headers_json["Content-Type"] = "application/json;charset=UTF-8"
        # Http request
        try:
            raw_res = requests.post(FIDO_DOLLAR_URL,
                                    data=data,
                                    headers=headers_json,
                                    cookies=self._cookies,
                                    timeout=self._timeout)
        except OSError:
            raise PyFidoError("Can not get fido dollar")
        # Get fido dollar
        try:
            fido_dollar_str = raw_res.json()\
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

    def _get_usage(self, account_number):
        """Get Fido usage.

        Get the following data
        - talk
        - text
        - data

        Roaming data is not supported yet
        """
        # Prepare data
        data = {"ctn": self.number,
                "language": "en-US",
                "accountNumber": account_number}
        # Http request
        try:
            raw_res = requests.post(USAGE_URL,
                                    data=data,
                                    headers=self._headers,
                                    cookies=self._cookies,
                                    timeout=self._timeout)
        except OSError:
            raise PyFidoError("Can not get usage")
        # Load answer as json
        try:
            output = raw_res.json()
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

    def fetch_data(self):
        """Fetch the latest data from Fido."""
        # Post login page
        self._post_login_page()
        # Get token
        token_uuid = self._get_token()
        # Get account number
        account_number = self._get_account_number(*token_uuid)
        # Get balance
        balance = self._get_balance(account_number)
        self._data['balance'] = balance
        # Get fido dollar
        fido_dollar = self._get_fido_dollar(account_number)
        self._data['fido_dollar'] = fido_dollar
        # Get usage
        usage = self._get_usage(account_number)
        # Update data
        self._data.update(usage)

    def get_data(self):
        """Return collected data"""
        return self._data
