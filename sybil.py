import csv
from tqdm import tqdm
import json
import time
from blacklist import BLACKLIST



def get_transactions_with_cap(min_cap, max_cap):
   print(f"Getting transactions with capital ({min_cap} - {max_cap})...")
   # stargate.csv is a file with all transactions in the bridge Stargate
   with open('stargate.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)

    writer_csv = csv.writer(open(f'{min_cap}_{max_cap}_cap_stargate.csv', 'w', newline=''))
    for row in tqdm(reader):
        try:
            if int(row[8].split(".")[0]) > min_cap and int(row[8].split(".")[0]) < max_cap:
                writer_csv.writerow(row)
        except:
            continue 


def get_wallets(min_cap, max_cap):
    print(f"Getting wallets with capital ({min_cap} - {max_cap})...")
    wallets = {}
    with open(f'{min_cap}_{max_cap}_cap_stargate.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in tqdm(reader):
            if row[4] not in BLACKLIST:
                if row[4] not in wallets:
                    wallets.update({row[4]: {'count': 1, 'quantity': [row[8]], 'timestamps': [row[5]]}})
                else:
                    wallets[row[4]]['count'] += 1
                    wallets[row[4]]['quantity'].append(row[8])
                    wallets[row[4]]['timestamps'].append(row[5])
    return wallets


def filter_1_transaction(wallets):
    print("Getting wallets with 1 transaction...")
    quantity_per_wallet = {}
    for wallet in wallets:
        if wallets[wallet]['count'] == 1:
            if wallets[wallet]['quantity'][0] not in quantity_per_wallet:
                quantity_per_wallet.update({wallets[wallet]['quantity'][0]: {'wallets': [wallet], 'timestamps': [wallets[wallet]['timestamps'][0]]}})
            else:
                quantity_per_wallet[wallets[wallet]['quantity'][0]]['wallets'].append(wallet)
                quantity_per_wallet[wallets[wallet]['quantity'][0]]['timestamps'].append(wallets[wallet]['timestamps'][0])
    return quantity_per_wallet


def get_sybils_network(quantity_per_wallet):
    sybils_networks = {}
    for quantity in quantity_per_wallet:
        if len(quantity_per_wallet[quantity]['wallets']) > 9:
            sybils_networks.update({quantity: {'count': len(quantity_per_wallet[quantity]['wallets']), 'wallets': quantity_per_wallet[quantity]['wallets'], 'timestamps': quantity_per_wallet[quantity]['timestamps']}})
    return sybils_networks

# Get transactions with certain cap
get_transactions_with_cap(0, 10)
get_transactions_with_cap(10, 100)
get_transactions_with_cap(100, 100000000000)

low_cap_wallets = get_wallets(0, 10)
medium_cap_wallets = get_wallets(10, 100)
high_cap_wallets = get_wallets(100, 100000000000)

low_cap_quantity_per_wallet = filter_1_transaction(low_cap_wallets)
medium_cap_quantity_per_wallet = filter_1_transaction(medium_cap_wallets)
high_cap_quantity_per_wallet = filter_1_transaction(high_cap_wallets)

low_cap_sybils_networks = get_sybils_network(low_cap_quantity_per_wallet)
medium_cap_sybils_networks = get_sybils_network(medium_cap_quantity_per_wallet)
high_cap_sybils_networks = get_sybils_network(high_cap_quantity_per_wallet)

low_cap_sybils_networks = dict(sorted(low_cap_sybils_networks.items(), key=lambda item: item[1]['count'], reverse=True))
medium_cap_sybils_networks = dict(sorted(medium_cap_sybils_networks.items(), key=lambda item: item[1]['count'], reverse=True))
high_cap_sybils_networks = dict(sorted(high_cap_sybils_networks.items(), key=lambda item: item[1]['count'], reverse=True))

report = open('report.md', 'w')
report.write('''---
name: Sybil Report
about: Report Sybil Activity on LayerZero
title: "[Sybil Report]"
labels: under review
assignees: LayerZero-GH

---
             
# Reported Addresses''')

report.write("\n## High capital (100$ - inf)")
n_cluster = 1
high_n_wallets = 0
for quantity in high_cap_sybils_networks:
    max_date = max(high_cap_sybils_networks[quantity]['timestamps'])[:-4]
    min_date = min(high_cap_sybils_networks[quantity]['timestamps'])[:-4]
    max_timestamp = time.mktime(time.strptime(max_date, '%Y-%m-%d %H:%M:%S'))
    min_timestamp = time.mktime(time.strptime(min_date, '%Y-%m-%d %H:%M:%S'))
    
    if (max_timestamp - min_timestamp) < 172800:
        count = high_cap_sybils_networks[quantity]['count']
        report.write(f"\n### Cluster #{n_cluster}: {count} wallets. {quantity}$ per wallet bridged. Activity between {min_date} and {max_date}")
        for wallet in high_cap_sybils_networks[quantity]['wallets']:
            report.write("\n" + wallet)
        report.write("\n")
        high_n_wallets += len(high_cap_sybils_networks[quantity]['wallets'])
        n_cluster += 1


report.write("\n\n## Medium capital (10$ - 100$)")
n_cluster = 1
medium_n_wallets = 0
for quantity in medium_cap_sybils_networks:
    max_date = max(medium_cap_sybils_networks[quantity]['timestamps'])[:-4]
    min_date = min(medium_cap_sybils_networks[quantity]['timestamps'])[:-4]
    max_timestamp = time.mktime(time.strptime(max_date, '%Y-%m-%d %H:%M:%S'))
    min_timestamp = time.mktime(time.strptime(min_date, '%Y-%m-%d %H:%M:%S'))
    
    if (max_timestamp - min_timestamp) < 172800:
        count = medium_cap_sybils_networks[quantity]['count']
        report.write(f"\n### Cluster #{n_cluster}: {count} wallets. {quantity}$ per wallet bridged. Activity between {min_date} and {max_date}")
        for wallet in medium_cap_sybils_networks[quantity]['wallets']:
            report.write("\n" + wallet)
        report.write("\n")
        medium_n_wallets += len(medium_cap_sybils_networks[quantity]['wallets'])
        n_cluster += 1

report.write("\n\n## Low capital (0$ - 10$)")
n_cluster = 1
low_n_wallets = 0
for quantity in low_cap_sybils_networks:
    max_date = max(low_cap_sybils_networks[quantity]['timestamps'])[:-4]
    min_date = min(low_cap_sybils_networks[quantity]['timestamps'])[:-4]
    max_timestamp = time.mktime(time.strptime(max_date, '%Y-%m-%d %H:%M:%S'))
    min_timestamp = time.mktime(time.strptime(min_date, '%Y-%m-%d %H:%M:%S'))
    
    if (max_timestamp - min_timestamp) < 172800:
        count = low_cap_sybils_networks[quantity]['count']
        report.write(f"\n### Cluster #{n_cluster}: {count} wallets. {quantity}$ per wallet bridged. Activity between {min_date} and {max_date}")
        for wallet in low_cap_sybils_networks[quantity]['wallets']:
            report.write("\n" + wallet)
        report.write("\n")
        low_n_wallets += len(low_cap_sybils_networks[quantity]['wallets'])
        n_cluster += 1


report.write("\n\n\n# Description")
report.write(f"\nThis report compiles {high_n_wallets + medium_n_wallets + low_n_wallets} different addresses ({high_n_wallets} with transactions of more than 100$, {medium_n_wallets} with transactions between 10 and 100$ and {low_n_wallets} of less than 10$) with sybil activity and they are not with HIGH PROBABILITY managed by individual users.")
report.write(f"\nIt focuses on looking for unusual transactions between blockchains with the Stargate bridge that are far from what a real and organic user would do.")

report.write("\n\n\n\n# Detailed Methodology & Walkthrough")
report.write("\nThe final goal was to find addresses with the following characteristics:")
report.write("\n1. Stargate bridge use. All wallets that do not used the Stargate bridge are automatically discarded. This project try to focus on people that farm the airdrop with a lot of wallets using Stargate.")
report.write("\n2. Identical amounts of money used on the bridge in 48-hour intervals. I am looking for groups of addresses that have used the bridge in a short period of time with the same amount of money.")
report.write("\n3. Addresses with low activity. I selected some groups of wallets that within the capitalization range have only made one transaction in Stargate.")
report.write("\n\nTo perform this search I first only look at the transactions that have used the Stargate bridge. Of the +127000000 messages extracted from the raw blockchain, I extract the +40000000 into a new CSV file, called stargate.csv. In all of these steps I use Python scripting.")
report.write("\nI split the stargate.csv in three groups, transactions from 0$ to 10$, from 10$ to 100$ and from 100$ to infinity. With observation I got the conclusion that this division makes sense, to prioritize the study of certain wallet clusters.")
report.write("\nI start with the extraction of the addresses, saving the number of Stargate bridge transactions, the amount of money in each transaction, and the timestamp of each of them.")
report.write("\nFrom the previous step I obtain a data dictionary, from which I only retrieve the wallets that have only one transaction. In this way, I reduce the probability that they are real user wallets by giving the bridge normal use.")
report.write("\nI group the selected wallets according to the amount used in the bridge in this single transaction, thus creating clusters of at least TEN wallets. Any grouping of less than ten wallets is discarded, in order to avoid posible false positives.")
report.write("\nAs a last check, the date and time of the cluster transactions are looked at, only selecting those that have not elapse more than 48 hours between the first and last transaction.")
report.write("\nChecking the activity of these wallets with the Arkham tool shows that with HIGH PROBABILITY all of these wallets have been used for massive airdrop farming, by a single person or entity, either manually or using automated tools.")
report.write("\n\nBelow is the link to the script made to extract the results:")
report.write("\nhttps://git...")

report.write("\n\n\n\n# Reward Address (If Eligible)")
report.write("\n0x27f68B4F36BCB859be81D47039c615Cd221D1140")
