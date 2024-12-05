import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

st.set_page_config(page_title="4sale Seasonality Analysis", page_icon=":bar_chart:", initial_sidebar_state="expanded")

st.sidebar.image("images.png", use_container_width=True)
with st.sidebar:
    selected = option_menu(
        "Navigation",
        ["Upload Data", "Info", "Monthly Analysis", "Weekly Analysis", "Daily Analysis",
         "Weekly in Month Analysis", "Hourly Analysis","Weekday Analysis","Insights"],
        icons=["cloud-upload", "info-circle", "calendar", "calendar-week", "calendar-day", "calendar-check", "clock","calendar-event","graph-up-arrow"],
        menu_icon="cast",
        default_index=0,
    )
st.sidebar.title("Filters")

final_data = pd.read_csv("final_data.csv")
level_1_options = final_data["Level-1"].unique()

# Global Level-1 filter
selected_level_1 = st.sidebar.selectbox("Select Level-1 Category", options=["All"] + list(level_1_options))

if selected == "Upload Data":
    st.header("Upload Data Files")

    transactions_file = st.file_uploader("Upload Transactions.csv", type=["csv"])
    listings_file = st.file_uploader("Upload ListingsCategories.csv", type=["csv"])

    if transactions_file and listings_file:

        transactions = pd.read_csv(transactions_file)
        listings = pd.read_csv(listings_file)
        listings["Level-1"] = listings["FULL_PATH"].str.split(" --_-- ").str[0]
        transactions = transactions.rename(columns={"CATEGORY_ID": "CAT_ID"})
        final_data = transactions.merge(listings[["CAT_ID", "Level-1"]], on="CAT_ID", how="left")

        # Save final_data for other modules
        final_data.to_csv("final_data.csv", index=False)

        st.success("Data uploaded and processed successfully! You can now proceed to analysis.")

elif selected == "Info":
    import info
    info.run()

elif selected == "Monthly Analysis":
    import monthly
    monthly.run(selected_level_1)

elif selected == "Weekly Analysis":
    import weekly
    weekly.run(selected_level_1)

elif selected == "Daily Analysis":
    import daily
    daily.run(selected_level_1)

elif selected == "Weekly in Month Analysis":
    import weekly_month
    weekly_month.run(selected_level_1)

elif selected == "Hourly Analysis":
    import hourly
    hourly.run(selected_level_1)

if selected == "Weekday Analysis":
    import weekday
    weekday.run(selected_level_1)

elif selected == "Insights":
    import insights
    insights.run()