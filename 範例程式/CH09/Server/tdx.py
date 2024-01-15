import time
import sys
if sys.implementation.name == 'micropython':
    import urequests as requests
else:
    import requests

class TDX():
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = ''
        self.expires_after = time.time()

    def get_token(self):
        if self.expires_after <= time.time():
            # print('get new access token:')
            token_url = 'https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token'
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            if sys.implementation.name == 'micropython':
                data = f'grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}'
            else:
                data = {
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                }
            response = requests.post(token_url, headers=headers, data=data)
            if response.status_code == 200:
                j = response.json()
                self.access_token = j['access_token']
                self.expires_after = time.time() + int(j['expires_in'])
                # print(response.status_code)
                # print('access token:'+ self.access_token[:6] + '...')
            else:
                print(f'error: {response.text}')
        return self.access_token

    def get_json(self, url):
        headers = {'authorization': f'Bearer {self.get_token()}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            j = response.json()
            response.close()
            return j
        else:
            return {
                'error_code': response.status_code,
                'text': response.text
            }