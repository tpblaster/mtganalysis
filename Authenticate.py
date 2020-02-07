import requests
import json


def authenticate_tcgplayer(client_public, client_secret):
    url = "https://api.tcgplayer.com/token"
    payload = "grant_type=client_credentials&client_id=" + str(client_public)+"&client_secret=" + str(client_secret)
    headers = {
        'Content-Type': "application/json",
        'User-Agent': "PostmanRuntime/7.20.1",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Postman-Token': "cbd44805-6be4-48b3-a9ea-3db105bfdf94,45208b7b-c801-4ea3-a65b-5dfc27c56d3e",
        'Host': "api.tcgplayer.com",
        'Accept-Encoding': "gzip, deflate",
        'Content-Length': "127",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    data = json.loads(response.text)
    if data["token_type"] == "bearer":
        return data["access_token"]
        print("auth successful")
    else:
        return 0



