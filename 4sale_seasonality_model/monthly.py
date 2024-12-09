import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA


def run(final_data, selected_level_1):
    st.header("Monthly Seasonality Analysis")

    try:
        # Ensure 'TIMESTAMP' is properly formatted
        final_data["TIMESTAMP"] = pd.to_datetime(
            final_data["TIMESTAMP"], errors="coerce"
        )
        if final_data["TIMESTAMP"].isnull().any():
            st.warning("Some rows have invalid timestamps and were coerced to NaT.")

        final_data["month"] = final_data["TIMESTAMP"].dt.month
        final_data["Level-1"] = (
            final_data["Level-1"].str.replace("--_--", "").str.strip()
        )

        # Filter for specific transaction type
        st.write("Filtering data for TRANSACTION_TYPE == 'Listing'...")
        final_data = final_data[final_data["TRANSACTION_TYPE"] == "Listing"]
        st.write(f"Data after filtering for 'Listing': {final_data.shape[0]} rows.")

        # Filter by selected level-1
        if selected_level_1 != "All":
            final_data = final_data[final_data["Level-1"] == selected_level_1]
            st.write(
                f"Data after filtering for selected Level-1: {final_data.shape[0]} rows."
            )

        if final_data.empty:
            st.warning(
                "No data available after filtering. Please check the selected Level-1 and transaction type."
            )
            return

        # Group by Level-1 and Month for monthly data
        st.write("Grouping data by Level-1 and month...")
        monthly_data = (
            final_data.groupby(["Level-1", "month"])
            .agg(revenue=("PRICE", "sum"), listings=("TRANSCATION_ID", "count"))
            .reset_index()
        )

        st.write(f"Monthly data after aggregation: {monthly_data.shape[0]} rows.")

        # Create seasonality index using ARIMA
        monthly_data["revenue_index"] = 0
        for level in monthly_data["Level-1"].unique():
            series = monthly_data[monthly_data["Level-1"] == level]["revenue"].fillna(0)

            try:
                model = ARIMA(series, order=(1, 1, 1))
                model_fit = model.fit()
                forecast = model_fit.fittedvalues
                forecast.iloc[0] = series.iloc[0]
                forecast_mean = forecast.mean()

                if forecast_mean > 1e-6:
                    monthly_data.loc[
                        monthly_data["Level-1"] == level, "revenue_index"
                    ] = (forecast / forecast_mean)
                else:
                    monthly_data.loc[
                        monthly_data["Level-1"] == level, "revenue_index"
                    ] = 1
            except Exception as e:
                st.warning(f"ARIMA failed for Level-1: {level} due to {e}")
                monthly_data.loc[monthly_data["Level-1"] == level, "revenue_index"] = 1

        # Add percentage change for growth analysis
        monthly_data["growth%"] = (
            monthly_data.groupby("Level-1")["revenue"].pct_change().fillna(0) * 100
        )

        # Colorize based on growth percentage
        def colorize(val):
            color = "green" if val > 0 else "red"
            return f"background-color: {color}; color: white"

        styled_df = monthly_data.style.applymap(colorize, subset=["growth%"])
        st.write("Processed Monthly Seasonality Data")
        st.dataframe(styled_df)

        # Generate heatmap for seasonality index
        st.write("Generating heatmap for seasonality index...")
        heatmap_data = monthly_data.pivot(
            index="Level-1", columns="month", values="revenue_index"
        )
        heatmap_data = heatmap_data.fillna(0)
        plt.figure(figsize=(12, 6))
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            cbar_kws={"label": "Seasonality Index"},
        )
        plt.title("Monthly Seasonality by Level-1")
        st.pyplot(plt)

        # Bar plot for monthly revenue
        st.write("Generating bar plot for monthly revenue...")
        month_bar = monthly_data.groupby("month")["revenue"].sum()
        plt.figure(figsize=(10, 6))
        month_bar.plot(kind="bar", color="skyblue")
        plt.title("Revenue by Month")
        plt.xlabel("Month")
        plt.ylabel("Total Revenue")
        plt.xticks(rotation=45)
        st.pyplot(plt)

    except Exception as e:
        st.error(f"An error occurred: {e}")
