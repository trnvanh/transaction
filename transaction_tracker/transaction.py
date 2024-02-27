import json
import pandas as pd
import matplotlib.pyplot as plt

# Load JSON data from file
with open('data.json') as f:
    data = json.load(f)

# Extract transaction details
transactions = data['transactions']['booked']

# Define function to categorize transactions
def categorize_transaction(transaction):
    if 'creditorName' not in transaction:
        return ['Other']
    #print("Processing transaction:", transaction['transactionId'])
    
    creditor_name = transaction.get('creditorName', "").lower()
    #debtor_name = transaction.get('debtorName', "").lower()

    amount = float(transaction['transactionAmount']['amount'])

    category_mappings = {
        'Groceries': ['lidl', 'k-supermarket', 'tokmanni', 'clas ohlson', 'normal', 'sale'],
        'Ordering Wolt': ['wolt'],
        'Coffee shop': ['espresso house', 'bacaro doppio', 'fazer'],
        'Boba': ['more tea', 'qualitea'],
        'Aasialainen kauppa': ['cindyn', 'golden crop', 'aasia market'],
        'Rent': lambda t: t.get('remittanceInformationUnstructured', "") == "Housing rent",
        #'Salary': lambda t: 'hoocee oy' in t.get('debtorName', ""),
        'Restaurant': ['luckiefun', 'ravintola', 'compass', 'momotoko'],
        'Subscription': ['telia', 'chegg', 'paypal', 'overleaf'],
        'Trip': lambda t: 'helsinki' in t.get('creditorName', ""),
        'Pharmacy': lambda t: 'ya tampere' in t.get('creditorName', ""),
        'Shopping': ['kauppa', 'carlings', 'glitter'],
        'Cinema': ['finnkino'],
    }

    categories = []
    for category, keywords_or_condition in category_mappings.items():
        if callable(keywords_or_condition):
            if keywords_or_condition(transaction):
                categories.append(category)
        elif any(keyword in creditor_name for keyword in keywords_or_condition):
            categories.append(category)

    return categories if categories else ['Other'], amount*(-1)

print("Number of transactions:", len(transactions))

# Filter transactions to only include those with a creditorName
filtered_transactions = [transaction for transaction in transactions if 'creditorName' in transaction]

# Categorize filtered transactions
categorized_transactions = [(transaction['transactionId'], transaction['creditorName'], *categorize_transaction(transaction)) 
                             for transaction in filtered_transactions]

# Save categorized transactions to a CSV file
df = pd.DataFrame(categorized_transactions, columns=['TransactionID', 'CreditorName', 'Category', 'Amount'])
df.to_csv('categorized_transactions.csv', index=False)

# Process categorized transactions
category_totals = {}
for _, _, categories, amount in categorized_transactions:
    for category in categories:
        category_totals[category] = category_totals.get(category, 0) + amount


# Plot the bar graph
categories = list(category_totals.keys())
totals = list(category_totals.values())

plt.figure(figsize=(10, 6))
plt.bar(categories, totals, color='skyblue')
plt.xlabel('Categories')
plt.ylabel('Total Money Spent (EUR)')
plt.title('Total Money Spent by Category')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()