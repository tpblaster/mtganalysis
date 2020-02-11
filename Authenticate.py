import requests
import json

from config import client_public, client_secret, access_code


def authenticate_tcgplayer(client_public, client_secret):
    url = "https://api.tcgplayer.com/token"
    payload = "grant_type=client_credentials&client_id=" + str(client_public) + "&client_secret=" + str(client_secret)
    response = requests.request("POST", url, data=payload)
    data = json.loads(response.text)
    if "access_token" in response.text:
        return data["access_token"]
        print("auth successful")
    else:
        return 0


def authenticate_tcgplayer_store(client_public, client_secret, access_code):
    bearer = authenticate_tcgplayer(client_public, client_secret)
    if bearer != 0:
        url = "http://api.tcgplayer.com/v1.32.0/app/authorize/" + str(access_code)
        headers = {
            'Authorization': "Bearer " + bearer
        }
        response = requests.request("POST", url, headers=headers)
        print(response.text)
    else:
        print("Store Auth Failed")
        return 0
authenticate_tcgplayer_store(client_public, client_secret, access_code)