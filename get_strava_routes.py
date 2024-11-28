import os
import requests
import json
from decouple import config
import requests
import time
import pprint

client_id = config('client_id')
client_secret = config('client_secret')
refresh_token = config('refresh_token')
access_token = config('access_token')


class StravaConnector:
    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self.expires_at = 0  # When the token will expire

    def get_access_token(self):
        # Refresh the token if expired
        if time.time() >= self.expires_at:
            token_url = "https://www.strava.com/api/v3/oauth/token"
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
            }
            response = requests.post(token_url, data=data)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch token: {response.json()}")
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
            self.expires_at = token_data['expires_at']
        return self.access_token

    def make_api_call(self, endpoint):
        # Ensure the token is valid
        token = self.get_access_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'https://www.strava.com/api/v3{endpoint}', headers=headers)
        if response.status_code != 200:
            raise Exception(f"API call failed: {response.json()}")
        return response.json()


strava = StravaConnector(client_id, client_secret, refresh_token)

# Get all the routes!!!
try:
    routes = strava.make_api_call('/athlete/routes')
    # print(json.dumps(routes, indent=2))
    for route in routes:
        route_id = route['id']
        with open(f'route_{route_id}.json', 'w') as f:
            json.dump(route, f, indent=2)
except Exception as e:
    print(f"Error! computer says NO - Failed to fetch routes: {e}")
