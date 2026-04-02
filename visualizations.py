import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

class SalesVisualizer:
    @staticmethod
    def create_hourly_sales_chart(df):
        """Create interactive hourly sales chart"""
        hourly = df.groupby('hour')['sales_amount'].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly['hour'], 
            y=hourly['sales_amount'],
            mode='lines+markers',
            name='Sales',
            line=dict(color='blue', width=2),
            marker=dict(size=8)
        ))
        fig.update_layout(
            title='Sales by Hour of Day',
            xaxis_title='Hour',
            yaxis_title='Total Sales ($)',
            hovermode='x unified',
            showlegend=True
        )
        
        # Add peak hour highlights
        fig.add_vrect(x0=11, x1=14, fillcolor="green", opacity=0.2, line_width=0, label="Lunch Peak")
        fig.add_vrect(x0=17, x1=21, fillcolor="orange", opacity=0.2, line_width=0, label="Dinner Peak")
        
        return fig
    
    @staticmethod
    def create_daily_heatmap(df):
        """Create daily-hourly sales heatmap"""
        pivot = df.groupby(['day_of_week', 'hour'])['sales_amount'].sum().reset_index()
        pivot_pivot = pivot.pivot(index='day_of_week', columns='hour', values='sales_amount')
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_pivot.index = day_names
        
        fig = px.imshow(
            pivot_pivot,
            labels=dict(x="Hour of Day", y="Day of Week", color="Sales ($)"),
            title="Sales Heatmap: Day vs Hour",
            color_continuous_scale='Viridis',
            aspect='auto'
        )
        return fig
    
    @staticmethod
    def create_location_comparison(df):
        """Create location performance comparison"""
        location_sales = df.groupby('location')['sales_amount'].sum().reset_index()
        fig = px.bar(
            location_sales,
            x='location',
            y='sales_amount',
            title='Total Sales by Location',
            color='sales_amount',
            color_continuous_scale='Blues'
        )
        fig.update_layout(xaxis_title='Location', yaxis_title='Total Sales ($)')
        return fig
    
    @staticmethod
    def create_seasonal_trend(df):
        """Create seasonal trend chart"""
        monthly = df.groupby(df['date'].dt.strftime('%Y-%m'))['sales_amount'].sum().reset_index()
        monthly.columns = ['month', 'sales_amount']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly['month'],
            y=monthly['sales_amount'],
            mode='lines+markers',
            name='Monthly Sales',
            line=dict(color='green', width=2),
            marker=dict(size=6)
        ))
        fig.update_layout(
            title='Seasonal Sales Trends',
            xaxis_title='Month',
            yaxis_title='Total Sales ($)',
            xaxis_tickangle=-45
        )
        return fig
    
    @staticmethod
    def create_category_pie(df):
        """Create category distribution pie chart"""
        category_sales = df.groupby('category')['sales_amount'].sum().reset_index()
        fig = px.pie(
            category_sales,
            values='sales_amount',
            names='category',
            title='Sales Distribution by Category',
            hole=0.3
        )
        return fig
    
    @staticmethod
    def create_weekend_comparison(df):
        """Compare weekend vs weekday patterns"""
        weekend_pattern = df.groupby(['is_weekend', 'hour'])['sales_amount'].mean().reset_index()
        
        fig = go.Figure()
        for weekend_status, color, name in [(True, 'red', 'Weekend'), (False, 'blue', 'Weekday')]:
            subset = weekend_pattern[weekend_pattern['is_weekend'] == weekend_status]
            fig.add_trace(go.Scatter(
                x=subset['hour'],
                y=subset['sales_amount'],
                mode='lines',
                name=name,
                line=dict(color=color, width=2)
            ))
        
        fig.update_layout(
            title='Weekday vs Weekend Sales Patterns',
            xaxis_title='Hour of Day',
            yaxis_title='Average Sales Amount ($)',
            hovermode='x unified'
        )
        return fig
    
    @staticmethod
    def create_staffing_heatmap(staffing_df):
        """Create staffing requirements heatmap"""
        staffing_pivot = staffing_df.pivot_table(
            values='required_staff', 
            index='location', 
            columns='hour', 
            aggfunc='mean'
        )
        
        fig = px.imshow(
            staffing_pivot,
            labels=dict(x="Hour of Day", y="Location", color="Required Staff"),
            title="Staffing Requirements Heatmap",
            color_continuous_scale='RdYlGn',
            aspect='auto'
        )
        return fig