import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class SalesDataGenerator:
    def __init__(self, random_seed=73):
        np.random.seed(random_seed)
        self.locations = ['Downtown', 'Uptown', 'Suburb East', 'Suburb West', 'Airport', 'Mall']
        self.menu_categories = ['Appetizers', 'Main Course', 'Beverages', 'Desserts', 'Specialty Drinks']
        
    def generate_dataset(self, n_observations=50000):
        """Generate synthetic sales data"""
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2023, 12, 31)
        date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        
        # Generate base data
        data = {
            'transaction_id': range(1, n_observations + 1),
            'date': np.random.choice(date_range, n_observations),
            'location': np.random.choice(self.locations, n_observations, 
                                        p=[0.25, 0.20, 0.15, 0.15, 0.15, 0.10]),
            'hour': np.random.choice(range(24), n_observations,
                                    p=[0.01]*8 + [0.05]*4 + [0.12]*4 + [0.04]*4 + [0.02]*4),
            'category': np.random.choice(self.menu_categories, n_observations,
                                        p=[0.20, 0.35, 0.25, 0.12, 0.08]),
            'num_customers': np.random.poisson(2.5, n_observations) + 1
        }
        
        df = pd.DataFrame(data)
        
        # Generate sales amounts
        df['sales_amount'] = df.apply(self._generate_sales_amount, axis=1)
        
        # Add time features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['year'] = df['date'].dt.year
        df['is_weekend'] = df['day_of_week'].isin([5, 6])
        
        return df
    
    def _generate_sales_amount(self, row):
        """Generate realistic sales amount based on multiple factors"""
        base_price = {
            'Appetizers': 12,
            'Main Course': 25,
            'Beverages': 6,
            'Desserts': 8,
            'Specialty Drinks': 11
        }[row['category']]
        
        hour_multiplier = 0.8 + (row['hour'] / 24) * 0.8
        month = row['date'].month
        
        if month in [12, 1, 2]:
            season_multiplier = 1.1
        elif month in [6, 7, 8]:
            season_multiplier = 1.2
        else:
            season_multiplier = 1.0
        
        location_multiplier = {
            'Downtown': 1.15, 'Airport': 1.25, 'Mall': 1.10,
            'Uptown': 1.05, 'Suburb East': 0.95, 'Suburb West': 0.95
        }[row['location']]
        
        amount = base_price * hour_multiplier * season_multiplier * location_multiplier * row['num_customers']
        amount += np.random.normal(0, amount * 0.15)
        return max(5, round(amount, 2))