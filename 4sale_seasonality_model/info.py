import pandas as pd
import streamlit as st

def run(final_data):
    st.header("Data Summary information ")
    st.subheader("Aggregation (Yearly and Monthly)")
    final_data_summary = calculate_summary(final_data, 'TIMESTAMP')
    final_data_summary['year'] = final_data_summary['year'].astype(str) 
    st.dataframe(final_data_summary)


def calculate_summary(df, date_col):
    df[date_col] = pd.to_datetime(df[date_col])
    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month

    summary = df.groupby(['year', 'month']).agg(
        total_transactions=('TRANSCATION_ID', 'count'),
        total_revenue=('PRICE', 'sum'),
        total_users=('USER_ID', 'nunique')
    ).reset_index()
    return summary

def calculate_yearly_totals(df, date_col):
    df[date_col] = pd.to_datetime(df[date_col])
    df['year'] = df[date_col].dt.year

    yearly_totals = df.groupby('year').agg(
        total_transactions=('TRANSCATION_ID', 'count'),
        total_revenue=('PRICE', 'sum'),
        total_users=('USER_ID', 'nunique')
    ).reset_index()
    return yearly_totals
