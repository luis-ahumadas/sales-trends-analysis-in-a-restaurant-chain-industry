import pandas as pd
import numpy as np

class SalesAnalytics:
    def __init__(self, df):
        self.df = df
        
    def get_peak_hours(self):
        """Identify peak hours based on sales"""
        hourly_sales = self.df.groupby('hour').agg({
            'sales_amount': 'sum',
            'transaction_id': 'count'
        }).round(2)
        hourly_sales.columns = ['total_sales', 'transaction_count']
        return hourly_sales.nlargest(3, 'total_sales')
    
    def get_daily_patterns(self):
        """Analyze daily sales patterns"""
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily = self.df.groupby('day_of_week').agg({
            'sales_amount': 'sum',
            'transaction_id': 'count',
            'num_customers': 'sum'
        }).round(2)
        daily.index = day_names
        return daily
    
    def get_seasonal_trends(self):
        """Analyze monthly and quarterly trends"""
        monthly = self.df.groupby('month').agg({
            'sales_amount': 'sum',
            'transaction_id': 'count'
        }).round(2)
        
        quarterly = self.df.groupby(['quarter', 'location'])['sales_amount'].sum().unstack()
        return monthly, quarterly
    
    def get_location_performance(self):
        """Compare location performance"""
        location_metrics = self.df.groupby('location').agg({
            'sales_amount': ['sum', 'mean', 'std'],
            'transaction_id': 'count',
            'num_customers': 'mean'
        }).round(2)
        location_metrics.columns = ['total_sales', 'avg_ticket', 'std_ticket', 'transactions', 'avg_party_size']
        return location_metrics.sort_values('total_sales', ascending=False)
    
    def get_category_analysis(self):
        """Analyze category performance by time and location"""
        category_hour = pd.crosstab(
            self.df['hour'], 
            self.df['category'], 
            values=self.df['sales_amount'], 
            aggfunc='sum'
        ).fillna(0)
        
        # Time period analysis
        self.df['time_period'] = pd.cut(
            self.df['hour'], 
            bins=[0, 11, 16, 21, 24], 
            labels=['Morning', 'Afternoon', 'Evening', 'Late Night']
        )
        category_time = pd.crosstab(
            self.df['time_period'], 
            self.df['category'], 
            values=self.df['sales_amount'], 
            aggfunc='sum'
        )
        
        return category_hour, category_time
    
    def get_staffing_recommendations(self):
        """Calculate staffing needs based on customer volume"""
        staffing = self.df.groupby(['location', 'day_of_week', 'hour']).agg({
            'transaction_id': 'count',
            'num_customers': 'sum'
        }).reset_index()
        
        # 1 staff per 15 customers per hour
        staffing['required_staff'] = np.ceil(staffing['num_customers'] / 15)
        
        peak_staffing = staffing[staffing['hour'].isin([12, 13, 18, 19])]
        peak_summary = peak_staffing.groupby(['location', 'hour'])['required_staff'].max().unstack()
        
        return staffing, peak_summary