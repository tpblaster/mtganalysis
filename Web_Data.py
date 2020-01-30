import sys

import requests
from bs4 import BeautifulSoup

import Authenticate
import Database_Interaction
import TCG_Card_Data
import pandas as pd


def get_ckz_data():
    url = 'http://www.cernyrytir.cz/katalog_vykup.php'
    response = requests.get(url)

    return response.text


def find_fields(response_text):
    soup_data = BeautifulSoup(response_text, "html.parser")
    form = soup_data.find('form')
    fields = form.findAll('input')
    select_data = form.findAll('select')
    form_data = dict((field.get('name'), field.get('value')) for field in fields)
    return form_data, select_data


def get_ckz_full_buylist():
    url = 'http://www.cernyrytir.cz/katalog_vykup.php'
    data = {
        'cena': 0,
        'edice': 'all',
        'notFoils': 'on',
        'zobrazit': 'Show'
    }
    response = requests.post(url, data=data)
    doc = BeautifulSoup(response.text, 'html.parser')
    return doc


def get_ckz_buylist_set(lowest_price, set_id):
    url = 'http://www.cernyrytir.cz/katalog_vykup.php'
    data = {
        'cena': str(lowest_price),
        'edice': str(set_id),
        'notFoils': 'on',
        'zobrazit': 'Show'
    }
    response = requests.post(url, data=data)
    doc = BeautifulSoup(response.text, 'html.parser')
    return doc


def parse_doc_data(table):
    all_data = []
    table_rows = table.find_all('tr')
    for tr in table_rows[3:]:
        td = tr.find_all('td')
        row = [i.text.strip() for i in td]
        first_row = row[0]
        row[0] = first_row.split(" ", 1)[0]
        row.insert(1, first_row.split(" ", 1)[1])
        all_data.append(row)
    return all_data


def build_ckz_set_database(cnx):
    cursor = cnx.cursor()
    set_data = []
    website_data = get_ckz_full_buylist()
    options = website_data.findAll('option')
    for i in range(1, len(options)):
        set_name = options[i].text.strip()
        print(set_name)
        set_value = options[i]["value"]
        print(set_value)
        abbreviation = get_ckz_set_abbreviation(set_value)
        if abbreviation is not None:
            set_data.append([set_name, set_value, abbreviation])
    for x in range(0, len(set_data)):
        query = """SELECT group_id FROM tcg_set_data WHERE set_name = '{}' or abbreviation = '{}'""".format(
            set_data[x][0], set_data[x][2])
        cursor.execute(query)
        ans = cursor.fetchall()
        if len(ans) > 1 or len(ans) == 0:
            # query = """UPDATE ckz_set_data SET tcg_group_id = {} WHERE set_id = """.format(ans[0][0])
            # cursor.execute(query)
            # cnx.commit()
            print(ans)
            print("matches")
            print(set_data[x][0])


def find_ckz_set_data(cnx):
    cursor = cnx.cursor()
    website_data = get_ckz_full_buylist()
    set_data = []
    options = website_data.findAll('option')
    query = """SELECT set_id FROM ckz_set_data"""

    for i in range(0, len(options)):
        set_name = options[i].text.strip()
        set_value = options[i]["value"]
        abbreviation = get_ckz_set_abbreviation(set_value)
        if abbreviation is not None:
            set_data.append([set_name, set_value, abbreviation])


def get_ckz_set_abbreviation(set_id):
    url = 'http://www.cernyrytir.cz/katalog_vykup.php'
    data = {
        'cena': 0,
        'edice': str(set_id),
        'notFoils': 'on',
        'zobrazit': 'Show'
    }
    response = requests.post(url, data=data)
    doc = BeautifulSoup(response.text, 'html.parser')
    table_data = doc.findAll('td')
    if len(table_data) > 1:
        return table_data[1].text.strip().split(" ", 1)[0]


def parse_buylist_compare_to_tcg(cnx, bearer):
    total_data = []
    cursor = cnx.cursor()
    query = """SELECT set_id, tcg_group_id FROM ckz_set_data"""
    cursor.execute(query)
    database_data = cursor.fetchall()
    for x in range(0, len(database_data)):
        buylist_data = parse_doc_data(get_ckz_buylist_set(0, database_data[x][0]))
        for y in buylist_data:
            query = """SELECT product_id FROM tcg_card_data WHERE group_id = {} AND card_name = \'{}\'""".format(
                database_data[x][1], y[1])
            cursor.execute(query)
            ans = cursor.fetchall()
            if len(ans) == 1:
                y.append(ans[0][0])
                sku = Database_Interaction.get_sku_from_product_id(cnx, ans[0][0], 1, 1, 1)
                if len(sku) > 0:
                    y.append(sku[0][0])
                    buylist_high = TCG_Card_Data.get_buylist_for_sku(bearer, sku[0][0])
                    if buylist_high is not None:
                        y.append(buylist_high)
                        y.append(round((1.1 * (float(y[3]))) - (1.1 * buylist_high), 2))
                    else:
                        y.append(0)
                        y.append(0)
                else:
                    y.append(0)
                    y.append(0)
                    y.append(0)
            else:
                y.append(0)
                y.append(0)
                y.append(0)
                y.append(0)
            print(y)
            total_data.append(y)
    df = pd.DataFrame(total_data)
    df.to_csv("1-30-20BuylistData3.csv", sep=',')
    return df


auth = Authenticate.authenticate_tcgplayer()
if auth != 0:
    bearer = auth
    print("tcg auth done")
else:
    print("tcg auth did not work")
    sys.exit()
cnx = Database_Interaction.connect_to_database("root", "<_=kE8dG;*Dmbz(G")
parse_buylist_compare_to_tcg(cnx, bearer)
