import streamlit as st
import pandas as pd
from info import calculate_yearly_totals
import matplotlib.pyplot as plt
import seaborn as sns

def run(final_data):
    st.title("Business Insights & Recommendations")
   
    
    
    st.subheader("Introduction")
    st.write("""
    This model is designed to calculate the seasonality for various granularities and estimate the expected growth based on historical data. 
    It uses ARIMA for seasonality forecasting and includes percentage growth analysis for each level of granularity.
    The model provides insights into revenue trends, helping to predict future performance and identify seasonality patterns.
    """)

    st.subheader("Challenges")
    st.write("""
    Based on the data below, the 2023 data is completely missing, and there is a clear decrease in transactions for 2022. 
    Due to the absence of recent data and the noticeable decrease in past transactions, we cannot fully rely on the model's accuracy 
    for future predictions. The missing data impacts the ability to make accurate forecasts and seasonality calculations.
    """)
    yearly_totals = calculate_yearly_totals(final_data, 'TIMESTAMP')
    yearly_totals['year'] = yearly_totals['year'].astype(str) 
    st.dataframe(yearly_totals)

    st.write("""
    From the above table, we can observe around a 90% increase in transactions in 2024 compared to 2022. 
    While this growth is notable, we must acknowledge the missing data for 2023. 
    Even though we see a significant increase, we cannot fully rely on this trend for future predictions 
    due to the lack of 2023 data, which limits the model's accuracy and reliability.
    """)
    
    st.write("""
         The chart below shows that October and November exhibit the best performance, with the highest revenue.
                   """)

    final_data["TIMESTAMP"] = pd.to_datetime(final_data["TIMESTAMP"])
    final_data["month"] = final_data["TIMESTAMP"].dt.month
    final_data["Level-1"] = final_data['Level-1'].str.replace('--_--', '').str.strip()
    final_data = final_data[final_data['TRANSACTION_TYPE'] == 'Listing']
    month_bar = final_data.groupby(["month"]).agg(
        revenue=("PRICE", "sum"))
    month_bar = month_bar.groupby('month')['revenue'].sum()

    # Plot a bar chart
    plt.figure(figsize=(10, 6))
    month_bar.plot(kind='bar', color='skyblue')
    plt.title('Revenue by monthly')
    plt.xlabel('month')
    plt.ylabel('Total Revenue')
    plt.xticks(rotation=45)
    st.pyplot(plt)
    
    st.subheader("Heatmap of Total Transactions (Year vs. Month)")

    st.write("""
         The chart below highlights significant missing data, which impacts the accuracy of any seasonality forecasting or pattern detection.
                   """)
    plot_heatmap(final_data, 'TIMESTAMP')

def plot_heatmap(df, date_col):
    df[date_col] = pd.to_datetime(df[date_col])
    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month

    heatmap_data = df.groupby(['year', 'month'])['TRANSCATION_ID'].count().unstack(fill_value=0)
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="YlGnBu", cbar_kws={'label': 'Total Transactions'})
    plt.xlabel("Month")
    plt.ylabel("Year")
    st.pyplot(plt)


    levels = st.session_state.final_data 
    levels["TIMESTAMP"] = pd.to_datetime(levels["TIMESTAMP"])
    levels["month"] = levels["TIMESTAMP"].dt.month
    levels["Level-1"] = levels['Level-1'].str.replace('--_--', '').str.strip()

    st.write("""
         The chart below highlights significant missing data on monthly level per category, which also impacts the accuracy of any seasonality forecasting or pattern detection.
                   """)
    
    st.subheader("Heatmap: Months vs. Level_1 Category (Total Transactions)")
    if 'Level-1' in levels.columns:
        plot_heatmap_level(levels, index='month', columns='Level-1', values='TRANSCATION_ID', aggfunc='count')
    else:
        st.warning("The 'level_1' column is not present in the dataset.")

def plot_heatmap_level(df, index, columns, values, aggfunc='sum'):
    pivot_table = pd.pivot_table(df, index=index, columns=columns, values=values, aggfunc=aggfunc)
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot_table, annot=True, fmt='.0f', cmap='YlGnBu', cbar=True)
    plt.xlabel(columns.capitalize())
    plt.ylabel(index.capitalize())
    st.pyplot(plt)






