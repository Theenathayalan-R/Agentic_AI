from typing import List, Dict, Any
import pandas as pd
from app.models.metadata import ColumnMetadata
# from trino.dbapi import connect as trino_connect # Uncomment for real Trino connection
# from app.core.config import settings # Uncomment for real config

# --- MOCK DATA (In a real app, this comes from Trino/Starburst queries and a metadata DB) ---
mock_domains_data = pd.DataFrame({
    'domain_id': ['d1', 'd2'],
    'domain_name': ['Wholesale', 'Retail'],
    'description': [
        'Data related to wholesale operations and transactions.',
        'Data related to retail operations, sales, and customer behavior.'
    ]
})

mock_datasets_data = pd.DataFrame({
    'dataset_id': ['ds1', 'ds2', 'ds3', 'ds4'],
    'domain_id': ['d1', 'd1', 'd2', 'd2'],
    'table_name': ['wholesale_orders', 'supplier_details', 'retail_sales', 'customer_profiles'],
    'description': [
        'A record of all wholesale orders placed by customers.',
        'Information about the suppliers we work with.',
        'Daily sales transactions from all retail stores.',
        'Detailed profiles of our retail customers.'
    ]
})

mock_metadata_data = {
    'ds1': pd.DataFrame({
        'column_name': ['order_id', 'customer_id', 'order_date', 'total_amount'],
        'data_type': ['varchar', 'varchar', 'timestamp', 'double'],
        'technical_description': [
            'Unique identifier for each order.',
            'Unique identifier for the customer placing the order.',
            'Date and time the order was placed.',
            'Total monetary value of the order.'
        ],
        'business_glossary': [
            'A unique number assigned to each order.',
            'The company or entity that purchased the goods.',
            'The date when the order was created in the system.',
            'The final, pre-tax total cost of the order.'
        ]
    }).to_dict(orient='records'),
    'ds2': pd.DataFrame({
        'column_name': ['supplier_id', 'supplier_name', 'contact_person', 'city'],
        'data_type': ['varchar', 'varchar', 'varchar', 'varchar'],
        'technical_description': [
            'Unique identifier for the supplier.',
            'Name of the supplying company.',
            'Primary contact person at the supplier.',
            'The city where the supplier is located.'
        ],
        'business_glossary': [
            'A unique code for each supplier.',
            'The legal name of the business providing products.',
            'The main point of contact for business communication.',
            'The city of the supplier\'s main office.'
        ]
    }).to_dict(orient='records'),
    'ds3': pd.DataFrame({
        'column_name': ['transaction_id', 'store_id', 'transaction_date', 'revenue'],
        'data_type': ['varchar', 'varchar', 'timestamp', 'double'],
        'technical_description': [
            'Unique identifier for each sales transaction.',
            'Identifier for the retail store.',
            'Date and time of the transaction.',
            'Revenue generated from the transaction.'
        ],
        'business_glossary': [
            'A unique number for each purchase at a retail store.',
            'The physical location where the sale occurred.',
            'The exact time of the customer purchase.',
            'The amount of money earned from the sale before returns.'
        ]
    }).to_dict(orient='records'),
    'ds4': pd.DataFrame({
        'column_name': ['customer_id', 'first_name', 'last_name', 'email', 'join_date'],
        'data_type': ['varchar', 'varchar', 'varchar', 'varchar', 'date'],
        'technical_description': [
            'Unique identifier for a customer.',
            'First name of the customer.',
            'Last name of the customer.',
            'Email address for communication.',
            'Date the customer profile was created.'
        ],
        'business_glossary': [
            'The unique identifier assigned to a retail shopper.',
            'The customer\'s given name.',
            'The customer\'s family name.',
            'The email address used for marketing and receipts.',
            'The date when the customer first interacted with our retail system.'
        ]
    }).to_dict(orient='records')
}


class TrinoClient:
    def __init__(self):
        # In a real scenario, initialize Trino connection here:
        # self.conn = trino_connect(
        #     host=settings.TRINO_HOST,
        #     port=settings.TRINO_PORT,
        #     user=settings.TRINO_USER,
        #     catalog=settings.TRINO_CATALOG,
        #     schema=settings.TRINO_SCHEMA,
        # )
        pass

    def _execute_query(self, query: str) -> List[Dict[str, Any]]:
        # In a real scenario, execute query and fetch results from Trino
        # cur = self.conn.cursor()
        # cur.execute(query)
        # return cur.fetchall()
        print(f"Executing mock Trino query: {query}")
        return [] # Return empty for mock

    def get_domains(self) -> pd.DataFrame:
        # In real scenario: query a metadata table or inferred from schemas
        return mock_domains_data

    def get_datasets_for_domain(self, domain_id: str) -> pd.DataFrame:
        # In real scenario: query metadata store for datasets by domain
        return mock_datasets_data[mock_datasets_data['domain_id'] == domain_id]

    def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        # In real scenario: query metadata store for dataset details
        info = mock_datasets_data[mock_datasets_data['dataset_id'] == dataset_id]
        return info.iloc[0].to_dict() if not info.empty else None

    def get_column_metadata(self, dataset_id: str) -> List[ColumnMetadata]:
        # In real scenario:
        # 1. Query Trino (DESCRIBE TABLE) for technical metadata
        # 2. Query your business glossary DB for business definitions
        # 3. Join them
        
        meta_list = mock_metadata_data.get(dataset_id, [])
        return [ColumnMetadata(**col) for col in meta_list]