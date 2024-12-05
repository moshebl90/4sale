import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose


def run(selected_level_1):
    st.header("Weekly Seasonality Analysis")

    final_data = pd.read_csv("final_data.csv")
    final_data["TIMESTAMP"] = pd.to_datetime(final_data["TIMESTAMP"])
    final_data["week"] = final_data["TIMESTAMP"].dt.isocalendar().week
    final_data["Level-1"] = final_data['Level-1'].str.replace('--_--', '').str.strip()
    final_data = final_data[final_data['TRANSACTION_TYPE'] == 'Listing']

    if selected_level_1 != "All":
        final_data = final_data[final_data["Level-1"] == selected_level_1]

    week_options = final_data["week"].unique()
    selected_week = st.sidebar.selectbox("Select Week", options=["All"] + sorted(week_options))

    if selected_week != "All":
        final_data = final_data[final_data["week"] == selected_week]

    # Group data
    weekly_data = final_data.groupby(["Level-1", "week"]).agg(
        revenue=("PRICE", "sum"),
        listings=("TRANSCATION_ID", "count")
    ).reset_index()

    weekly_data["revenue_index"] = (
        weekly_data.groupby("Level-1")["revenue"].transform(lambda x: x / x.mean())
    )
    weekly_data["growth%"] = weekly_data["revenue_index"].apply(lambda x: round((x - 1) * 100, 2))

    def colorize(val):
        color = 'green' if val > 0 else 'red'
        return f'background-color: {color}; color: white'

    styled_df = weekly_data.style.applymap(colorize, subset=["growth%"])
    st.write("Processed Weekly Seasonality Data")
    st.dataframe(styled_df)

    heatmap_data = weekly_data.pivot(index="Level-1", columns="week", values="revenue_index")
    plt.figure(figsize=(14, 7))
    sns.heatmap(heatmap_data, annot=False, cmap="coolwarm")
    st.pyplot(plt)

    arima_data = weekly_data[weekly_data["Level-1"] == selected_level_1][["week", "revenue"]]
    arima_data = arima_data.set_index("week")

    if len(arima_data) >= 104:
        st.write(f"Seasonality Analysis for {selected_level_1}")

        try:
            decomposition = seasonal_decompose(arima_data["revenue"], model="additive", period=52)
            st.write("Seasonal Component")
            st.line_chart(decomposition.seasonal)
        except Exception as e:
            st.error(f"Error during seasonal decomposition: {e}")

        try:
            model = ARIMA(arima_data["revenue"], order=(1, 1, 1))
            arima_result = model.fit()

            st.write("ARIMA Model Summary")
            st.text(arima_result.summary())

            forecast = arima_result.forecast(steps=5)
            st.write("Forecast for Next 5 Weeks")
            st.line_chart(forecast)
        except Exception as e:
            st.error(f"Error fitting ARIMA model: {e}")
    else:
        st.warning(
            "No selected level-1 category or Not enough data for seasonal decomposition or ARIMA analysis. At least 104 observations are required."
        )
        st.write("Here are some aggregated insights from the available data:")
        st.bar_chart(arima_data["revenue"])