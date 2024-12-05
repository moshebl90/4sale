import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

def run(final_data, selected_level_1):
    st.header("Monthly Seasonality Analysis")

    # Preprocess final_data
    final_data["TIMESTAMP"] = pd.to_datetime(final_data["TIMESTAMP"])
    final_data["month"] = final_data["TIMESTAMP"].dt.month
    final_data["Level-1"] = final_data['Level-1'].str.replace('--_--', '').str.strip()
    final_data = final_data[final_data['TRANSACTION_TYPE'] == 'Listing']
    if selected_level_1 != "All":
        final_data = final_data[final_data["Level-1"] == selected_level_1]


    monthly_data = final_data.groupby(["Level-1", "month"]).agg(
        revenue=("PRICE", "sum"),
        listings=("TRANSCATION_ID", "count")
    ).reset_index()

    monthly_data["revenue_index"] = 0

    # Iterate over each Level-1 category
    for level in monthly_data["Level-1"].unique():
        series = monthly_data[monthly_data["Level-1"] == level]["revenue"].fillna(0)

        try:
            # Fit ARIMA model
            model = ARIMA(series, order=(1, 1, 1))
            model_fit = model.fit()
            forecast = model_fit.fittedvalues
            forecast.iloc[0] = series.iloc[0]
            forecast_mean = forecast.mean()
            if forecast_mean > 1e-6:
                monthly_data.loc[
                    monthly_data["Level-1"] == level, "revenue_index"
                ] = forecast / forecast_mean
            else:

                monthly_data.loc[
                    monthly_data["Level-1"] == level, "revenue_index"
                ] = 1

        except Exception as e:
            # Log an error message if ARIMA fails
            st.warning(f"ARIMA failed for Level-1: {level} due to {e}")
            # Set revenue index to 1 as fallback
            monthly_data.loc[
                monthly_data["Level-1"] == level, "revenue_index"
            ] = 1
    # Calculate growth percentage
    monthly_data["growth%"] = (
            monthly_data.groupby("Level-1")["revenue"].pct_change().fillna(0) * 100
    )

    def colorize(val):
        color = 'green' if val > 0 else 'red'
        return f'background-color: {color}; color: white'

    styled_df = monthly_data.style.applymap(colorize, subset=["growth%"])
    st.write("Processed Monthly Seasonality Data")
    st.dataframe(styled_df)


    heatmap_data = monthly_data.pivot(index="Level-1", columns="month", values="revenue_index")
    heatmap_data = heatmap_data.fillna(0)
    heatmap_data = heatmap_data.astype(float)
    # Plot heatmap
    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", cbar_kws={'label': 'Seasonality Index'})
    plt.title("Monthly Seasonality by Level-1")
    st.pyplot(plt)
