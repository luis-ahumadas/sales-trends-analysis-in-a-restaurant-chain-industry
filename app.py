import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

from data_generator import SalesDataGenerator
from analytics import SalesAnalytics
from visualizations import SalesVisualizer

# Page configuration
st.set_page_config(
    page_title="Restaurant Sales Analytics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2C3E50;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F0F2F6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    with st.spinner('Generating sales data...'):
        generator = SalesDataGenerator(random_seed=73)
        st.session_state.data = generator.generate_dataset(50000)
        st.session_state.analytics = SalesAnalytics(st.session_state.data)

# Sidebar filters
st.sidebar.title("🔍 Filters")

# Date range filter
min_date = st.session_state.data['date'].min()
max_date = st.session_state.data['date'].max()
date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Location filter
locations = ['All'] + list(st.session_state.data['location'].unique())
selected_locations = st.sidebar.multiselect(
    "Select Locations",
    locations,
    default=['All']
)

# Category filter
categories = ['All'] + list(st.session_state.data['category'].unique())
selected_categories = st.sidebar.multiselect(
    "Select Categories",
    categories,
    default=['All']
)

# Apply filters
filtered_data = st.session_state.data.copy()
if len(date_range) == 2:
    filtered_data = filtered_data[
        (filtered_data['date'] >= pd.to_datetime(date_range[0])) &
        (filtered_data['date'] <= pd.to_datetime(date_range[1]))
    ]

if 'All' not in selected_locations:
    filtered_data = filtered_data[filtered_data['location'].isin(selected_locations)]

if 'All' not in selected_categories:
    filtered_data = filtered_data[filtered_data['category'].isin(selected_categories)]

# Main header
st.markdown('<div class="main-header">🍽️ Restaurant Chain Sales Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown("---")

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_data['sales_amount'].sum()
    st.metric("Total Sales", f"${total_sales:,.2f}")

with col2:
    avg_ticket = filtered_data['sales_amount'].mean()
    st.metric("Average Ticket", f"${avg_ticket:.2f}")

with col3:
    total_transactions = len(filtered_data)
    st.metric("Total Transactions", f"{total_transactions:,}")

with col4:
    unique_locations = filtered_data['location'].nunique()
    st.metric("Active Locations", unique_locations)

st.markdown("---")

# Tab layout
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Temporal Analysis",
    "📍 Location Insights",
    "🍽️ Menu Analytics",
    "👥 Staffing & Inventory",
    "📈 Executive Summary"
])

# Tab 1: Temporal Analysis
with tab1:
    st.markdown('<div class="sub-header">Peak Hours Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly sales chart
        hourly_chart = SalesVisualizer.create_hourly_sales_chart(filtered_data)
        st.plotly_chart(hourly_chart, use_container_width=True)
        
        # Peak hours info
        peak_hours = st.session_state.analytics.get_peak_hours()
        st.info(f"**Peak Hours:** {', '.join(map(str, peak_hours.index.tolist()))}")
    
    with col2:
        # Weekend comparison
        weekend_chart = SalesVisualizer.create_weekend_comparison(filtered_data)
        st.plotly_chart(weekend_chart, use_container_width=True)
    
    # Seasonal trends
    st.markdown('<div class="sub-header">Seasonal Trends</div>', unsafe_allow_html=True)
    seasonal_chart = SalesVisualizer.create_seasonal_trend(filtered_data)
    st.plotly_chart(seasonal_chart, use_container_width=True)
    
    # Daily heatmap
    st.markdown('<div class="sub-header">Daily Sales Heatmap</div>', unsafe_allow_html=True)
    heatmap = SalesVisualizer.create_daily_heatmap(filtered_data)
    st.plotly_chart(heatmap, use_container_width=True)

# Tab 2: Location Insights
with tab2:
    st.markdown('<div class="sub-header">Location Performance</div>', unsafe_allow_html=True)
    
    # Location comparison
    location_chart = SalesVisualizer.create_location_comparison(filtered_data)
    st.plotly_chart(location_chart, use_container_width=True)
    
    # Location metrics table
    location_metrics = st.session_state.analytics.get_location_performance()
    st.dataframe(location_metrics.style.format({
        'total_sales': '${:,.2f}',
        'avg_ticket': '${:.2f}',
        'transactions': '{:,}',
        'avg_party_size': '{:.1f}'
    }), use_container_width=True)

# Tab 3: Menu Analytics
with tab3:
    st.markdown('<div class="sub-header">Menu Category Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Category distribution
        category_pie = SalesVisualizer.create_category_pie(filtered_data)
        st.plotly_chart(category_pie, use_container_width=True)
    
    with col2:
        # Category performance over time
        category_hour, _ = st.session_state.analytics.get_category_analysis()
        fig = go.Figure()
        for category in category_hour.columns:
            fig.add_trace(go.Scatter(
                x=category_hour.index,
                y=category_hour[category],
                name=category,
                mode='lines'
            ))
        fig.update_layout(
            title='Category Sales Throughout the Day',
            xaxis_title='Hour',
            yaxis_title='Sales ($)',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

# Tab 4: Staffing & Inventory
with tab4:
    st.markdown('<div class="sub-header">Staffing Recommendations</div>', unsafe_allow_html=True)
    
    staffing_df, peak_staffing = st.session_state.analytics.get_staffing_recommendations()
    
    # Staffing heatmap
    staffing_heatmap = SalesVisualizer.create_staffing_heatmap(staffing_df)
    st.plotly_chart(staffing_heatmap, use_container_width=True)
    
    # Staffing recommendations
    st.markdown("### Peak Hour Staffing Needs")
    st.dataframe(peak_staffing, use_container_width=True)
    
    # Inventory recommendations
    st.markdown("### Inventory Recommendations")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Based on Peak Hour Analysis:**
        - 🥩 Main courses: 45% of inventory allocation
        - 🥤 Beverages: Consistent 25% baseline
        - 🍷 Specialty drinks: Focus on evening hours
        - 🍰 Desserts: Increase for dinner service
        """)
    
    with col2:
        st.warning("""
        **Seasonal Adjustments:**
        - ☀️ Summer (June-Aug): +30% inventory
        - 🎄 December: +15% inventory
        - ❄️ Jan-Feb: -20% inventory
        - 📦 Order 3-5 days before peak periods
        """)

# Tab 5: Executive Summary
with tab5:
    st.markdown('<div class="sub-header">Executive Dashboard</div>', unsafe_allow_html=True)
    
    # Key insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Key Opportunities")
        st.success("""
        - **Lunch vs Dinner Strategy**: Differentiate service models
        - **Weekend Brunch**: Untapped revenue opportunity
        - **Location Optimization**: Location-specific strategies
        - **Category Management**: Time-based menu highlighting
        """)
    
    with col2:
        st.markdown("### ⚠️ Risk Areas")
        st.error("""
        - **Monday Slowdown**: 25% below average
        - **January-February**: Seasonal low period
        - **Afternoon Dip (3-4 PM)**: Revenue gap
        - **Suburban Winter**: Weather sensitivity
        """)
    
    # Recommendations
    st.markdown("### 📋 Actionable Recommendations")
    
    rec_df = pd.DataFrame({
        'Priority': ['High', 'High', 'Medium', 'Medium', 'Low'],
        'Action': [
            'Implement split shifts for peak hours',
            'Launch Monday/Tuesday promotions',
            'Develop seasonal menu rotations',
            'Create weekend brunch program',
            'Optimize inventory for summer peak'
        ],
        'Expected Impact': [
            '15-20% labor efficiency',
            '10-15% Monday sales lift',
            '8-12% revenue increase',
            '20% weekend sales growth',
            '25% waste reduction'
        ]
    })
    st.dataframe(rec_df, use_container_width=True, hide_index=True)
    
    # Financial projections
    st.markdown("### 💰 Projected Financial Impact")
    metrics = {
        'Metric': ['Labor Cost Reduction', 'Food Waste Reduction', 'Revenue Increase', 'Total Annual Impact'],
        'Current': ['$1,000,000', '$200,000', '$5,000,000', '$6,200,000'],
        'Projected': ['$850,000', '$160,000', '$5,500,000', '$6,510,000'],
        'Savings/Gain': ['$150,000', '$40,000', '$500,000', '$690,000']
    }
    impact_df = pd.DataFrame(metrics)
    st.dataframe(impact_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    🚀 Powered by Streamlit | Data-driven insights for restaurant excellence
    </div>
    """,
    unsafe_allow_html=True
)