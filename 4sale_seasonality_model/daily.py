import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

def run(final_data, selected_level_1):
    st.header("Daily Seasonality Analysis")
    final_data = st.session_state.final_data 
    final_data["TIMESTAMP"] = pd.to_datetime(final_data["TIMESTAMP"])
    final_data["day"] = final_data["TIMESTAMP"].dt.day
    final_data["Level-1"] = final_data['Level-1'].str.replace('--_--', '').str.strip()
    final_data = final_data[final_data['TRANSACTION_TYPE'] == 'Listing']

    if selected_level_1 != "All":
        final_data = final_data[final_data["Level-1"] == selected_level_1]

    daily_data = final_data.groupby(["Level-1", "day"]).agg(
        revenue=("PRICE", "sum"),
        listings=("TRANSCATION_ID", "count")
    ).reset_index()

    daily_data["revenue_index"] = 0
    for level in daily_data["Level-1"].unique():
        series = daily_data[daily_data["Level-1"] == level]["revenue"].fillna(0)

        try:
            model = ARIMA(series, order=(1, 1, 1))
            model_fit = model.fit()
            forecast = model_fit.fittedvalues
            forecast.iloc[0] = series.iloc[0]
            forecast_mean = forecast.mean()
            if forecast_mean > 1e-6:  
                daily_data.loc[
                    daily_data["Level-1"] == level, "revenue_index"
                ] = forecast / forecast_mean
            else:
                daily_data.loc[
                    daily_data["Level-1"] == level, "revenue_index"
                ] = 1

        except Exception as e:
            st.warning(f"ARIMA failed for Level-1: {level} due to {e}")
            daily_data.loc[
                daily_data["Level-1
