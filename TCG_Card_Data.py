import requests
import json


def get_category_groups(bearer, offset, category):
    url = "http://api.tcgplayer.com/v1.35.0/catalog/categories/" + str(category) + "/groups?offset=" + str(offset) + ""
    headers = {
        'Authorization': "Bearer " + bearer,
    }
    response = requests.request("GET", url, headers=headers)
    data = json.loads(response.text)
    if data["success"] and len(data["results"]) > 0:
        return data
    else:
        print(data)
        print("request did not work")
        return 0


def get_number_of_groups(bearer, category):
    url = "http://api.tcgplayer.com/v1.35.0/catalog/categories/" + str(category) + "/groups"
    headers = {
        'Authorization': "Bearer " + bearer,
    }
    response = requests.request("GET", url, headers=headers)
    data = json.loads(response.text)
    return int(data["totalItems"])


def get_category_group_all(bearer, category):
    x = 0
    group_data = []
    while True:
        data = get_category_groups(bearer, x, category)
        if data == 0:
            break
        else:
            x = x + 10
            y = 0
            for (data["GroupId"]) in (data["results"]):
                group_data.append(data["results"][y])
                y = y + 1
    return group_data


def get_group_cards(bearer, group, offset):
    url = "http://api.tcgplayer.com/v1.32.0/catalog/products?categoryId=1&groupId=" + str(
        group) + "&productTypes=cards&offset=" + str(offset)
    headers = {
        'Authorization': "Bearer " + bearer
    }
    response = requests.request("GET", url, headers=headers)
    data = json.loads(response.text)
    if data["success"]:
        return data["results"]
    else:
        return 0


def get_group_cards_all(bearer, group):
    x = 0
    group_data = []
    while True:
        data = get_group_cards(bearer, group, x)
        if data == 0:
            break
        else:
            x = x + 10
            for y in range(0, (len(data))):
                group_data.append(data[y])
    return group_data


def get_direct_low_from_product_id(bearer, product_id, foil):
    url = "http://api.tcgplayer.com/v1.35.0/pricing/product/" + str(product_id)
    headers = {
        'Authorization': "Bearer " + bearer
    }
    response = requests.request("GET", url, headers=headers)
    data = json.loads(response.text)
    if len(data["results"]) > 1:
        for x in range(0, len(data["results"])):
            if (data["results"][x])["subTypeName"] == foil:
                price = (data["results"][x])["directLowPrice"]
        if price is not None:
            return price
    else:
        price = (data["results"][0])["directLowPrice"]
        return price


def get_skus_from_product_id(bearer, product_id):
    url = "http://api.tcgplayer.com/v1.32.0/catalog/products/{}/skus".format(product_id)
    payload = {}
    headers = {
        'Authorization': "Bearer " + bearer
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)
    if len(data["results"]) > 0:
        return data["results"]
    else:
        print("some product id is broken")
        return 0


def get_group_details(bearer, group):
    url = "http://api.tcgplayer.com/v1.35.0/catalog/groups/{}".format(group)
    headers = {
        'Authorization': "Bearer " + bearer
    }
    response = requests.request("GET", url, headers=headers)
    data = json.loads(response.text)
    return data["results"]


def get_product_details(bearer, product_id):
    url = "http://api.tcgplayer.com/v1.32.0/catalog/products/" + str(product_id)
    headers = {
        'Authorization': "Bearer " + bearer
    }
    response = requests.request("GET", url, headers=headers)
    data = json.loads(response.text)
    return data["results"]


def get_buylist_for_sku(bearer, sku):
    url = "http://api.tcgplayer.com/v1.32.0/pricing/buy/sku/" + str(sku)
    headers = {
        'Authorization': "Bearer " + bearer
    }
    response = requests.request("GET", url, headers=headers)
    data = json.loads(response.text)
    return data["results"][0]["prices"]["high"]
