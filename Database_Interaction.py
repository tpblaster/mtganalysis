import mysql.connector

from TCG_Card_Data import get_group_cards_all, get_skus_from_product_id, get_category_group_all, get_group_details, \
    get_product_details


def connect_to_database(client_public: object, client_secret: object) -> object:
    cnx = mysql.connector.connect(user=client_public, password=client_secret,
                                  host="localhost",
                                  database='tcgdata')
    return cnx


def build_tcg_set_data(cnx, group_data):
    cursor = cnx.cursor()
    for x in range(0, len(group_data)):
        if "'" in (group_data[x])["name"]:
            name = (group_data[x])["name"].replace("'", "''")
        else:
            name = (group_data[x])["name"]
        query = """insert into tcg_set_data (group_id, set_name, abbreviation, is_supplemental, published_on, modified_on, category_id)
            VALUES ({}, \'{}\', \'{}\', {}, \'{}\', \'{}\', {})""".format((group_data[x])["groupId"], name,
                                                                          (group_data[x])["abbreviation"],
                                                                          (group_data[x])["isSupplemental"],
                                                                          (group_data[x])["publishedOn"],
                                                                          (group_data[x])["modifiedOn"],
                                                                          (group_data[x])["categoryId"])
        cursor.execute(query)
        cnx.commit()


def get_all_tcg_groups(cnx):
    query = """select group_id, set_id from tcg_set_data"""
    cursor = cnx.cursor()
    cursor.execute(query)
    my_result = cursor.fetchall()
    return my_result


def build_tcg_card_data(bearer, cnx):
    group_data = get_all_tcg_groups(cnx)
    for x in group_data:
        card_data = get_group_cards_all(bearer, x[0])
        for y in range(0, len(card_data)):
            insert_card(cnx, card_data[y], x[1])


def insert_card(cnx, card, database_set_id):
    cursor = cnx.cursor()
    if "'" in card["name"]:
        name = (card["name"]).replace("'", "''")
    else:
        name = (card["name"])
    query = """insert into tcg_card_data(product_id, card_name, clean_name, image_url, category_id, group_id, url, modified_on, database_set_id) VALUES ({}, \'{}\', \'{}\', \'{}\', {}, {}, \'{}\', \'{}\', {})""".format(
        card["productId"], name, card["cleanName"], card["imageUrl"], card["categoryId"], card["groupId"], card["url"],
        card["modifiedOn"], database_set_id)
    cursor.execute(query)
    cnx.commit()


def get_product_and_group_id_from_name_only(cnx, card_name):
    if "'" in card_name:
        card_name = card_name.replace("'", "''")
    cursor = cnx.cursor()
    query = """SELECT product_id, group_id FROM tcg_card_data WHERE card_name = \'{}\';""".format(card_name)
    cursor.execute(query)
    ans = cursor.fetchall()
    return ans


def get_product_and_group_id_from_name_and_set(cnx, card_name, set_name):
    database_set_id = get_database_set_id_from_set_name(cnx, set_name)
    cursor = cnx.cursor()
    if len(database_set_id) == 1:
        if "'" in card_name:
            card_name = card_name.replace("'", "''")
        card_name = card_name.strip()
        query = """select product_id, group_id from tcg_card_data where card_name = \'{}\' and database_set_id = {};""".format(
            card_name, database_set_id[0][0])
        cursor.execute(query)
        ans = cursor.fetchall()
        if len(ans) > 0:
            return ans
        else:
            return None
    elif len(database_set_id) > 1:
        print(set_name)
        print("too many sets")
        return None
    else:
        print(set_name)
        print("no sets found")
        return None


def get_database_set_id_from_set_name(cnx, set_name):
    if "'" in set_name:
        set_name = set_name.replace("'", "''")
    cursor = cnx.cursor()
    query = """select set_id from tcg_set_data where set_name = \'{}\' or amazon_name = \'{}\';""".format(set_name,
                                                                                                          set_name)
    cursor.execute(query)
    ans = cursor.fetchall()
    return ans


def build_sku_database(cnx, bearer):
    cursor = cnx.cursor()
    query = """select product_id from tcg_card_data where product_id not in (select product_id from tcg_sku_data);"""
    cursor.execute(query)
    ans = cursor.fetchall()
    for x in range(0, len(ans)):
        data = get_skus_from_product_id(bearer, ans[x][0])
        if data != 0:
            for y in range(0, len(data)):
                insert_data_into_sku_database(cnx, data[y])


def insert_data_into_sku_database(cnx, data):
    cursor = cnx.cursor()
    query = """INSERT INTO tcg_sku_data(product_id, sku_id, language_id, printing_id, condition_id)
    VALUES({}, {}, {}, {}, {})""".format(data["productId"], data["skuId"], data["languageId"], data["printingId"],
                                         data["conditionId"])
    print(query)
    cursor.execute(query)
    cnx.commit()


def get_sku_from_product_id(cnx, productId, languageId, printingId, conditionId):
    cursor = cnx.cursor()
    query = """SELECT sku_id FROM tcg_sku_data WHERE condition_id = {} AND product_id = {} AND language_id = {} AND 
    printing_id = {}""".format(conditionId, productId, languageId, printingId)
    cursor.execute(query)
    ans = cursor.fetchall()
    return ans


def get_nm_non_foil_sku_from_product_id(cnx, product_id):
    cursor = cnx.cursor()
    query = """SELECT sku_id FROM tcg_sku_data WHERE product_id = {} AND language_id = 1 AND condition_id = 1 AND 
    printing_id = 1""".format(product_id)
    cursor.execute(query)
    ans = cursor.fetchall()
    return ans


def get_groups_and_modified_dates(cnx):
    cursor = cnx.cursor()
    query = """SELECT group_id, modified_on FROM tcg_set_data"""
    cursor.execute(query)
    ans = cursor.fetchall()
    return ans


# Takes a list of groups that are missing and inserts them, then finds the database id and returns them
def update_group_database(bearer, cnx, differences):
    cursor = cnx.cursor()
    database_set_id_list = []
    for i in differences:
        group_data = get_group_details(bearer, i)
        build_tcg_set_data(cnx, group_data)
        query = """SELECT set_id FROM tcg_set_data WHERE group_id = {}""".format(i)
        cursor.execute(query)
        ans = cursor.fetchall()
        database_set_id_list.append(ans[0][0])
        print("new database set id inserted: {}".format(ans[0][0]))
    return database_set_id_list


def update_database(cnx, bearer):
    # Gets and creates list of groups and modified dates from the database
    ans = get_groups_and_modified_dates(cnx)
    all_groups_from_database = [row[0] for row in ans]
    # Gets and creates list of groups and modified dates from the API
    groups = get_category_group_all(bearer, 1)
    all_groups_from_api = []
    for x in range(0, len(groups)):
        all_groups_from_api.append(groups[x]["groupId"])
    # Finds missing groups from database using the list from the API
    differences = [elem for elem in all_groups_from_api if elem not in all_groups_from_database]
    print("differences")
    print(differences)

    # Inserts cards that are from sets that were previously missing
    if len(differences) > 0:
        # Enters new groups into the set database and gets the new database set it for each one
        database_set_id_list = update_group_database(bearer, cnx, differences)
        for x in range(0, len(differences)):
            card_data = get_group_cards_all(bearer, differences[x])
            if card_data != 0:
                for y in range(0, len(card_data)):
                    insert_card(cnx, card_data[y], database_set_id_list[x])
    group_changes = find_changes_in_modified_dates_groups(cnx, bearer)
    modified_cards = find_modified_cards(bearer, group_changes, cnx)
    missing_cards = find_missing_cards(bearer, group_changes, cnx)
    for i in modified_cards:
        update_card(cnx, i, get_product_details(bearer, i))
        print("updated " + str(i))
        remove_sku_from_database(cnx, i)
    for i in missing_cards:
        missing_card_data = get_product_details(bearer, i)
        print("updated " + str(i))
        insert_card(cnx, missing_card_data, get_database_set_id_from_group_id(cnx, missing_card_data["groupId"]))
    print("Building Sku Database")
    build_sku_database(cnx, bearer)
    print("Done")


# Finds all groups that have a different modified date than what the API returns
def find_changes_in_modified_dates_groups(cnx, bearer):
    cursor = cnx.cursor()
    query = """SELECT modified_on, group_id FROM tcg_set_data"""
    cursor.execute(query)
    group_and_modified_data_from_database = cursor.fetchall()
    groups = get_category_group_all(bearer, 1)
    all_modified_dates_from_api = []
    group_id_for_changes = []
    for x in range(0, len(groups)):
        all_modified_dates_from_api.append([groups[x]["modifiedOn"], groups[x]["groupId"]])
    for y in range(0, len(all_modified_dates_from_api)):
        for x in range(0, len(group_and_modified_data_from_database)):
            if all_modified_dates_from_api[y][1] == group_and_modified_data_from_database[x][1]:
                if all_modified_dates_from_api[y][0] != group_and_modified_data_from_database[x][0]:
                    print("updates needed for " + str(all_modified_dates_from_api[y][1]))
                    print(all_modified_dates_from_api[y][0])
                    group_id_for_changes.append(all_modified_dates_from_api[y][1])
                break
    return group_id_for_changes


# Pass a complete list of all groups that have changes, returns a list of all cards that have been modified
def find_modified_cards(bearer, changed_sets, cnx):
    card_change = []
    cursor = cnx.cursor()
    for i in changed_sets:
        print(i)
        query = """SELECT modified_on, product_id FROM tcg_card_data WHERE group_id = {};""".format(i)
        cursor.execute(query)
        ans = cursor.fetchall()
        api_group_cards = get_group_cards_all(bearer, i)
        if api_group_cards != 0:
            for x in range(0, len(api_group_cards)):
                for z in range(0, len(ans)):
                    if api_group_cards[x]["productId"] == ans[z][1]:
                        if api_group_cards[x]["modifiedOn"] != ans[z][0]:
                            card_change.append(api_group_cards[x]["productId"])
    return card_change


# Pass a complete list of all groups that have changes, returns all missing productIds
def find_missing_cards(bearer, changed_sets, cnx):
    missing_cards = []
    cursor = cnx.cursor()
    for i in changed_sets:
        query = """SELECT product_id FROM tcg_card_data WHERE group_id = {};""".format(i)
        cursor.execute(query)
        ans = cursor.fetchall()
        api_group_cards = get_group_cards_all(bearer, i)
        api_product_id = []
        for x in range(0, len(api_group_cards)):
            api_product_id.append(api_group_cards[x]["productId"])
        database_product_id = []
        for x in range(0, len(ans)):
            database_product_id.append(ans[x][0])
        if api_group_cards != 0:
            differences = [elem for elem in api_product_id if elem not in database_product_id]
            if len(differences) > 0:
                missing_cards.append(differences)
                print("missing: " + str(differences))
    return missing_cards


def get_database_set_id_from_group_id(cnx, group):
    cursor = cnx.cursor()
    query = """SELECT set_id FROM tcg_set_data WHERE group_id = {}""".format(group)
    cursor.execute(query)
    ans = cursor.fetchall()
    return ans[0][0]


def update_card(cnx, product_id, card_data):
    cursor = cnx.cursor()
    if "'" in card_data[0]["name"]:
        name = (card_data[0]["name"]).replace("'", "''")
    else:
        name = (card_data[0]["name"])
    query = """UPDATE tcg_card_data SET card_name = \'{}\', clean_name = \'{}\', image_url = \'{}\', category_id = {}, group_id = {}, url = \'{}\', modified_on = \'{}\' WHERE product_id = {};""".format(
        name, card_data[0]["cleanName"], card_data[0]["imageUrl"], card_data[0]["categoryId"], card_data[0]["groupId"],
        card_data[0]["url"], card_data[0]["modifiedOn"], product_id)
    cursor.execute(query)
    cnx.commit()


# Pass a product id and remove skus all from the database
def remove_sku_from_database(cnx, product_id):
    cursor = cnx.cursor()
    query = """DELETE FROM tcg_sku_data WHERE product_id = {}""".format(product_id)
    cursor.execute(query)
    cnx.commit()
