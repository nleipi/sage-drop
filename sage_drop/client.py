import requests
from typing import Literal
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin
from datetime import date, datetime, timezone


class Client():
    def __init__(self, base_url: str, user_name: str, password: str):
        self.base_url = base_url
        self.user_name = user_name
        self.password = password
        self.session = requests.Session()

        self.login()

    def get_url(self, path):
        return urljoin(self.base_url, path)

    def login(self):
        login_url = self.get_url('mportal/Login.aspx')
        res = self.session.get(login_url)
        soup = BeautifulSoup(res.text, features='html.parser')

        user_input = soup.form.find('input', attrs={'type': 'text'})
        user_input.attrs['value'] = self.user_name

        password_input = soup.form.find('input', attrs={'type': 'password'})
        password_input.attrs['value'] = self.password

        data = defaultdict(list)
        for tag in soup.form.find_all('input'):
            data[tag.attrs.get('name', '')].append(tag.attrs.get('value', ''))

        self.session.post(urljoin(self.base_url, 'hrportalapi//Authorization'),
                          json={
                              'Username': self.user_name,
                              'Password': self.password,
                              'NtAuthorization': False,
                              }
                          )
        self.session.post(urljoin(self.base_url,
                                  'hrportalapi//Security/Calculate'))

        res = self.session.post(login_url, data)
        soup = BeautifulSoup(res.text, features='html.parser')

        res = self.session.get(self.get_url('hrportalapi/AuthorizationInfo'))
        self.auth_info = res.json()

    def get_current_time(self):
        res = self.session.get(self.get_url(
            'hrportalapi/Configuration/CurrentTime'))
        return datetime.fromisoformat(res.text.strip('\"'))

    def get_balance(self):
        key_date = self.get_current_time().astimezone(timezone.utc)
        params = {
                'mdnr': self.auth_info['EmployeeKey']['MdNr'],
                'annr': self.auth_info['EmployeeKey']['AnNr'],
                'keyDate': key_date.isoformat()
                }
        res = self.session.get(self.get_url(
            'hrportalapi/Time/AccountsBooking'), params=params)
        return res.json()

    def stamp_time(self, stamp_type: Literal['Come', 'Go'],
                   location: int, additional_input: int | None = None):
        # GET http://sage.fabfab.de/
        # http://sage.fabfab.de/hrportalapi/Time/StampTime?type=Go&additionalInputId=1&placeofworkid=1
        params = {
                'type': stamp_type,
                'placeofworkid': location,
                }
        if additional_input is not None:
            params['additionalInput'] = additional_input
        res = self.session.post(self.get_url(
            'hrportalapi/Time/StampTime'), params=params)
        if not res.text == 'true':
            raise Exception(res.text)

    def time_pairs(self, date_from: date, date_to: date):
        params = {
                'MdNr': self.auth_info['EmployeeKey']['MdNr'],
                'AnNr': self.auth_info['EmployeeKey']['AnNr'],
                'from': date_from.strftime('%Y-%m-%dT%H:%M:%S'),
                'to': date_to.strftime('%Y-%m-%dT%H:%M:%S'),
                }
        res = self.session.get(self.get_url(
            'hrportalapi/Time/TimePairs'), params=params)
        return res.json()

    def get_places_of_work(self):
        res = self.session.get(self.get_url(
            'hrportalapi/Time/Common/PlacesOfWork'))
        return res.json()
