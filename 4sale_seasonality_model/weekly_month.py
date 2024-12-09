import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA


def run(final_data, selected_level_1):
    st.header("Weekly in Month Seasonality Analysis")

    final_data = st.session_state.final_data 
    final_data["TIMESTAMP"] = pd.to_datetime(final_data["TIMESTAMP"])
    final_data["week_of_month"] = final_data["TIMESTAMP"].dt.day // 7 + 1
    final_data["month"] = final_data["TIMESTAMP"].dt.month
    final_data["Level-1"] = final_data["Level-1"].str.replace('--_--', '').str.strip()
    final_data = final_data[final_data['TRANSACTION_TYPE'] == 'Listing']

    if selected_level_1 != "All":
        final_data = final_data[final_data["Level-1"] == selected_level_1]

    month_options = final_data["month"].unique()
    selected_month = st.sidebar.selectbox("Select Month", options=["All"] + sorted(month_options))

    if selected_month != "All":
        final_data = final_data[final_data["month"] == selected_month]

    weekly_month_data = final_data.groupby(["Level-1", "week_of_month"]).agg(
        revenue=("PRICE", "sum"),
        listings=("TRANSCATION_ID", "count")
    ).reset_index()

    weekly_month_data["revenue_index"] = (
        weekly_month_data.groupby("Level-1")["revenue"].transform(lambda x: x / x.mean())
    )
    weekly_month_data["growth%"] = weekly_month_data["revenue_index"].apply(lambda x: round((x - 1) * 100, 2))

    def colorize(val):
        color = 'green' if val > 0 else 'red'
        return f'background-color: {color}; color: white'

    styled_df = weekly_month_data.style.applymap(colorize, subset=["growth%"])
    st.write("Processed Weekly Seasonality data within a Month Data")
    st.dataframe(styled_df)


    heatmap_data = weekly_month_data.pivot(index="Level-1", columns="week_of_month", values="revenue_index")


    heatmap_data = heatmap_data.fillna(0)
    heatmap_data = heatmap_data.astype(float)

    # Plot heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", cbar_kws={'label': 'Seasonality Index'})
    plt.title("Weekly Seasonality Within a Month")
    st.pyplot(plt)

    st.subheader("ARIMA-Based Seasonality Analysis")
    arima_data = weekly_month_data.groupby("week_of_month")["revenue"].sum()
    st.write("ARIMA Input Data (Revenue per Week of Month):")
    st.line_chart(arima_data)

    try:
        model = ARIMA(arima_data, order=(1, 1, 1))
        arima_result = model.fit()
        #st.write("ARIMA Summary:")
        #st.text(arima_result.summary())

        forecast = arima_result.forecast(steps=4)
        st.write("Forecast for the Next 4 Weeks:")
        st.write("You must select your target month -1 for before forecast")
        st.write(pd.DataFrame({"Week": ["Week 1", "Week 2", "Week 3", "Week 4"], "Forecasted Revenue": forecast}))
    except Exception as e:
        st.error(f"ARIMA model could not be fitted: {e}")

    week_bar = weekly_month_data.groupby('week_of_month')['revenue'].sum()

    # Plot a bar chart
    plt.figure(figsize=(10, 6))
    week_bar.plot(kind='bar', color='skyblue')
    plt.title('Revenue by week of month')
    plt.xlabel('week_of_month')
    plt.ylabel('Total Revenue')
    plt.xticks(rotation=45)
    st.pyplot(plt)
