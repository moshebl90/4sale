import pandas as pd
import streamlit as st

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

def run():
    st.header("Data Information")

    try:
        final_data = pd.read_csv("final_data.csv")
    except FileNotFoundError:
        st.error("Please upload the required data files first!")
        return

    st.subheader("Data Summary (Yearly and Monthly)")
    final_data_summary = calculate_summary(final_data, 'TIMESTAMP')
    st.dataframe(final_data_summary)

