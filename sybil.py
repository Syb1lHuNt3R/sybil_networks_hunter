import csv
from tqdm import tqdm
import json


initial_list = open('initialList.txt', 'r').readlines()
BLACKLIST = []
[BLACKLIST.append(wallet.strip()) for wallet in initial_list]


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
            if row[4] not in wallets:
                wallets.update({row[4]: {'count': 1, 'quantity': [row[8]], 'timestamps': [row[5]]}})
            else:
                wallets[row[4]]['count'] += 1
                wallets[row[4]]['quantity'].append(row[8])
                wallets[row[4]]['timestamps'].append(row[5])
    return wallets


def filter_n_transaction(wallets):
    print("Getting wallets with n transaction...")
    quantity_per_wallet = {}
    for wallet in tqdm(wallets):
        if wallets[wallet]['count'] > 1 and wallet not in BLACKLIST:
            sorted_quantities = sorted(wallets[wallet]['quantity'])
            if str(sorted_quantities) not in quantity_per_wallet:
                quantity_per_wallet.update({str(sorted_quantities): {'wallets': [wallet], 'timestamps': [wallets[wallet]['timestamps']]}})
            else:
                quantity_per_wallet[str(sorted_quantities)]['wallets'].append(wallet)
                quantity_per_wallet[str(sorted_quantities)]['timestamps'].append(wallets[wallet]['timestamps'])
    return quantity_per_wallet


def get_sybils_network(quantity_per_wallet):
    sybils_networks = {}
    for quantity in tqdm(quantity_per_wallet):
        if len(quantity_per_wallet[quantity]['wallets']) > 99:
            sybils_networks.update({quantity: {'count': len(quantity_per_wallet[quantity]['wallets']), 'wallets': quantity_per_wallet[quantity]['wallets'], 'timestamps': quantity_per_wallet[quantity]['timestamps']}})
    return sybils_networks

# Get transactions with certain cap
get_transactions_with_cap(0, 10)
get_transactions_with_cap(10, 100)
get_transactions_with_cap(100, 100000000000)

low_cap_wallets = get_wallets(0, 10)
medium_cap_wallets = get_wallets(10, 100)
high_cap_wallets = get_wallets(100, 100000000000)

low_cap_quantity_per_wallet = filter_n_transaction(low_cap_wallets)
medium_cap_quantity_per_wallet = filter_n_transaction(medium_cap_wallets)
high_cap_quantity_per_wallet = filter_n_transaction(high_cap_wallets)

low_cap_json = open('low_cap_sybils_networks.json', 'w')
low_cap_json.write(json.dumps(low_cap_quantity_per_wallet))
medium_cap_json = open('medium_cap_sybils_networks.json', 'w')
medium_cap_json.write(json.dumps(medium_cap_quantity_per_wallet))
high_cap_json = open('high_cap_sybils_networks.json', 'w')
high_cap_json.write(json.dumps(high_cap_quantity_per_wallet))



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
    count = high_cap_sybils_networks[quantity]['count']
    report.write(f"\n### Cluster #{n_cluster}: {count} wallets. {quantity}$ per wallet bridged.")
    for wallet in high_cap_sybils_networks[quantity]['wallets']:
        report.write("\n" + wallet)
    report.write("\n")
    high_n_wallets += len(high_cap_sybils_networks[quantity]['wallets'])
    n_cluster += 1


report.write("\n\n## Medium capital (10$ - 100$)")
n_cluster = 1
medium_n_wallets = 0
for quantity in medium_cap_sybils_networks:
    count = medium_cap_sybils_networks[quantity]['count']
    report.write(f"\n### Cluster #{n_cluster}: {count} wallets. {quantity}$ per wallet bridged.")
    for wallet in medium_cap_sybils_networks[quantity]['wallets']:
        report.write("\n" + wallet)
    report.write("\n")
    medium_n_wallets += len(medium_cap_sybils_networks[quantity]['wallets'])
    n_cluster += 1

report.write("\n\n## Low capital (0$ - 10$)")
n_cluster = 1
low_n_wallets = 0
for quantity in low_cap_sybils_networks:
    count = low_cap_sybils_networks[quantity]['count']
    report.write(f"\n### Cluster #{n_cluster}: {count} wallets. {quantity}$ per wallet bridged.")
    for wallet in low_cap_sybils_networks[quantity]['wallets']:
        report.write("\n" + wallet)
    report.write("\n")
    low_n_wallets += len(low_cap_sybils_networks[quantity]['wallets'])
    n_cluster += 1


report.write("\n\n\n# Description")
report.write(f"\nThis report compiles {high_n_wallets + medium_n_wallets + low_n_wallets} different addresses ({high_n_wallets} with transactions of more than 100$, {medium_n_wallets} with transactions between 10 and 100$ and {low_n_wallets} of less than 10$) with sybil activity and they are not with HIGH PROBABILITY managed by individual users.")
report.write(f"\nIt focuses...") # REDACTED
