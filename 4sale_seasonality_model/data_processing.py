import pandas as pd

def process_uploaded_data(transactions, categories):
    categories['Level-1'] = categories['FULL_PATH'].str.split('--_--').str[0].str.strip()
    categories['Level-1'] = categories['Level-1'].str.replace('--_--', '').str.strip()
    enriched_data = pd.merge(
        transactions,
        categories[['CAT_ID', 'Level-1']],
        left_on='CATEGORY_ID',
        right_on='CAT_ID',
        how='left'
    )

    enriched_data['TIMESTAMP'] = pd.to_datetime(enriched_data['TIMESTAMP'])
    return enriched_data