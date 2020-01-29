import sys

import pandas as pd
import Authenticate
import Database_Interaction


print("starting")

auth = Authenticate.authenticate_tcgplayer()
if auth != 0:
    bearer = auth
    print("tcg auth done")
else:
    print("tcg auth did not work")
    sys.exit()


cnx = Database_Interaction.connect_to_database("root", "<_=kE8dG;*Dmbz(G")

Database_Interaction.update_database(cnx, bearer)

sys.exit()
csv_data = Import_CSV.read_csv_from_path(r"C:\Users\proma\Documents\RobotCheck2.csv")

data = CSV_Interaction.break_down_amazon_data(csv_data, cnx)
data_for_frame = CSV_Interaction.compare_tcg_to_amazon(data, bearer)
df = pd.DataFrame(data_for_frame, columns=['Name', 'TCG', 'Amazon'])
df.to_csv("tcg vs amazon 8th.csv", sep=',')
