import re

from pandas import notnull

import Database_Interaction
import TCG_Card_Data


class cardData:
    def __init__(self, card_name, amazon_price, stock, group_id, product_id, foil):
        self.card_name = card_name
        self.amazon_price = amazon_price
        self.stock = stock
        self.group_id = group_id
        self.product_id = product_id
        self.foil = foil


def break_down_amazon_data(data, cnx):
    total_data = []
    for x in range(0, len(data)):
        print_statement = "{} of {}".format(x, len(data))
        print(print_statement)
        name_data = (data.loc[x])[0]
        if "Magic: the Gathering -" in name_data:
            name_data = name_data.replace("Magic: the Gathering - ", "")
        elif "Magic: The Gathering -" in name_data:
            name_data = name_data.replace("Magic: The Gathering - ", "")
        elif "Magic The Gathering - " in name_data:
            name_data = name_data.replace("Magic The Gathering - ", "")
        elif "Wizards of the Coast" in name_data:
            name_data = name_data.replace("Wizards of the Coast ", "")
        elif "Magic: the Gathering" in name_data:
            name_data = name_data.replace("Magic: the Gathering ", "")
        elif "Magic: the Gathering" in name_data:
            name_data = name_data.replace("Magic The Gathering ", "")
        elif "Magic: The Gathering" in name_data:
            name_data = name_data.replace("Magic: The Gathering ", "")
        elif "Magic The Gathering" in name_data:
            name_data = name_data.replace("Magic The Gathering ", "")
        elif "Magic Singles " in name_data:
            name_data = name_data.replace("Magic Singles ", "")

        if "39;" in name_data:
            name_data = name_data.replace("39;", "'")
        name_data = re.sub("[\(\[].*?[\)\]]", "", name_data)
        name_data = name_data.split(" - ")
        regex = re.compile(r'[0-9]+/[0-9]+')
        name_data = [i for i in name_data if not regex.match(i)]
        name_data = list(filter(None, name_data))
        if "Rare" in name_data:
            name_data.remove("Rare")
        elif "Mythic" in name_data:
            name_data.remove("Mythic")
        elif "Common" in name_data:
            name_data.remove("Common")
        elif "Uncommon" in name_data:
            name_data.remove("Uncommon")

        if "R" in name_data:
            name_data.remove("R")
        if "M" in name_data:
            name_data.remove("M")
        if "U" in name_data:
            name_data.remove("U")
        if "C" in name_data:
            name_data.remove("C")

        if "Planeswalker Deck Exclusive" in name_data:
            name_data.remove("Planeswalker Deck Exclusive")
        if "Brawl Deck Exclusive" in name_data:
            name_data.remove("Brawl Deck Exclusive")
        if "Collector Pack Exclusive" in name_data:
            name_data.remove("Collector Pack Exclusive")
        if "Planeswalker Deck Exclusives" in name_data:
            name_data.remove("Planeswalker Deck Exclusives")
        if "Store Championships Promo" in name_data:
            name_data.remove("Store Championships Promo")

        if len(name_data) == 1:
            card = amazon_data_just_name(name_data[0], cnx, (data.loc[x])[1], (data.loc[x])[2])
            if card is not None:
                total_data.append(card)
        elif len(name_data) == 2:
            card = amazon_data_name_and_set(name_data[0], name_data[1], cnx, (data.loc[x])[1], (data.loc[x])[2])
            if card is not None:
                total_data.append(card)
            else:
                print(name_data[0])
                print("doesn't work")
        elif len(name_data) == 3:
            # TODO finish 3 long name data management
            if "Showcase" in name_data:
                name_data.remove("Showcase")
                card = amazon_data_name_and_set(name_data[0] + " (Showcase)", name_data[1], cnx, (data.loc[x])[1],
                                                (data.loc[x])[2])
                if card is not None:
                    total_data.append(card)
                else:
                    print(name_data[0])
                    print("doesn't work")
            elif "Foil" in name_data:
                name_data.remove("Foil")
                card = amazon_data_name_and_set_foil(name_data[0], name_data[1], cnx, (data.loc[x])[1],
                                                     (data.loc[x])[2])
                if card is not None:
                    total_data.append(card)
                else:
                    print(name_data[0])
                    print("doesn't work")
            else:
                print(name_data)
    return total_data


def amazon_data_just_name(name, cnx, price_info, stock_info):
    database_info = Database_Interaction.get_product_and_group_id_from_name_only(cnx, name)
    if len(database_info) == 1:
        if notnull(stock_info):
            stock = re.sub("\D", "", stock_info)
        else:
            stock = 21
        price = price_info.replace("$", "")
        return cardData(name, price, stock, database_info[0][1], database_info[0][0], 0)
    else:
        return None


def amazon_data_name_and_set(name, mtg_set, cnx, price_info, stock_info):
    data = Database_Interaction.get_product_and_group_id_from_name_and_set(cnx, name, mtg_set)

    if data is not None:
        if notnull(stock_info):
            stock = re.sub("\D", "", stock_info)
        else:
            stock = 21
        price = price_info.replace("$", "")

        return cardData(name, price, stock, data[0][1], data[0][0], 0)


def amazon_data_name_and_set_foil(name, mtg_set, cnx, price_info, stock_info):
    data = Database_Interaction.get_product_and_group_id_from_name_and_set(cnx, name, mtg_set)

    if data is not None:
        if notnull(stock_info):
            stock = re.sub("\D", "", stock_info)
        else:
            stock = 21
        price = price_info.replace("$", "")

        return cardData(name, price, stock, data[0][1], data[0][0], 1)


def compare_tcg_to_amazon(data, bearer):
    data_for_frame = []
    for x in range(0, len(data)):
        if data[x].foil == 0:
            tcgprice = TCG_Card_Data.get_direct_low_from_product_id(bearer, data[x].product_id, "Normal")
        else:
            tcgprice = TCG_Card_Data.get_direct_low_from_product_id(bearer, data[x].product_id, "Foil")
        if str(tcgprice) == "None":
            directLow = 0
        else:
            directLow = tcgprice
        nextdata = [data[x].card_name, tcgprice, data[x].amazon_price]
        data_for_frame.append(nextdata)
        print_statement = "{} of {}".format(x, len(data))
        print(print_statement)
    return data_for_frame


