import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

def run(final_data, selected_level_1):
    st.header("Daily Seasonality Analysis")
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
            if forecast_mean > 1e-6:  # Prevent division by zero
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
                daily_data["Level-1"] == level, "revenue_index"
            ] = 1  # Fallback: Set revenue_index to 1

    # Calculate growth percentage
    daily_data["growth%"] = daily_data["revenue_index"].apply(lambda x: round((x - 1) * 100, 2))


    def colorize(val):
        color = 'green' if val > 0 else 'red'
        return f'background-color: {color}; color: white'

    styled_df = daily_data.style.applymap(colorize, subset=["growth%"])
    st.write("Processed Daily Seasonality Data:")
    st.dataframe(styled_df)

    heatmap_data = daily_data.pivot(index="Level-1", columns="day", values="revenue_index")
    heatmap_data = heatmap_data.fillna(0).astype(float)

    # Plot heatmap
    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", cbar_kws={'label': 'Seasonality Index'})
    plt.title("Daily Seasonality by Level-1")
    st.pyplot(plt)

    day_bar = daily_data.groupby('day')['revenue'].sum()

    # Plot a bar chart
    plt.figure(figsize=(12, 6))
    day_bar.plot(kind='bar', color='skyblue')
    plt.title('Revenue by daily')
    plt.xlabel('day')
    plt.ylabel('Total Revenue')
    plt.xticks(rotation=45)
    st.pyplot(plt)
