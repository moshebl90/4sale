import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# Set up the page
st.set_page_config(page_title="4sale Seasonality Analysis", page_icon=":bar_chart:", initial_sidebar_state="expanded")

# Sidebar image
st.sidebar.image("4sale_seasonality_model/images.png", use_container_width=True)

# Sidebar menu options
with st.sidebar:
    selected = option_menu(
        "Navigation",
        ["Upload Data", "Info", "Monthly Analysis", "Weekly Analysis", "Daily Analysis",
         "Weekly in Month Analysis", "Hourly Analysis", "Weekday Analysis", "Insights"],
        icons=["cloud-upload", "info-circle", "calendar", "calendar-week", "calendar-day", "calendar-check", "clock", "calendar-event", "graph-up-arrow"],
        menu_icon="cast",
        default_index=0,
    )

# Sidebar filters (conditionally rendered after data upload)
if "final_data" in st.session_state:
    level_1_options = st.session_state.final_data["Level-1"].unique()
    selected_level_1 = st.sidebar.selectbox("Select Level-1 Category", options=["All"] + list(level_1_options))
else:
    st.sidebar.warning("Please upload data first to access filters.")

# Navigation options
if selected == "Upload Data":
    st.header("Upload Data Files")
    
    # File upload widgets
    transactions_file = st.file_uploader("Upload Transactions.csv", type=["csv"])
    listings_file = st.file_uploader("Upload ListingsCategories.csv", type=["csv"])
    
    # Process uploaded files
    if transactions_file and listings_file:
        transactions = pd.read_csv(transactions_file)
        listings = pd.read_csv(listings_file)

        # Data cleaning and merging
        listings["Level-1"] = listings["FULL_PATH"].str.split(" --_-- ").str[0]
        transactions = transactions.rename(columns={"CATEGORY_ID": "CAT_ID"})
        final_data = transactions.merge(listings[["CAT_ID", "Level-1"]], on="CAT_ID", how="left")

        # Save data in session state
        st.session_state.final_data = final_data

        # Success message
        st.success("Data uploaded and processed successfully! You can now proceed to analysis.")
    else:
        st.info("Please upload both Transactions.csv and ListingsCategories.csv.")

elif "final_data" not in st.session_state:
    # Handle missing data for other pages
    st.warning("Please upload data first to access this page.")

elif selected == "Info":
    import info
    info.run(st.session_state.final_data)

elif selected == "Monthly Analysis":
    import monthly
    monthly.run(st.session_state.final_data, selected_level_1)

elif selected == "Weekly Analysis":
    import weekly
    weekly.run(st.session_state.final_data, selected_level_1)

elif selected == "Daily Analysis":
    import daily
    daily.run(st.session_state.final_data, selected_level_1)

elif selected == "Weekly in Month Analysis":
    import weekly_month
    weekly_month.run(st.session_state.final_data, selected_level_1)

elif selected == "Hourly Analysis":
    import hourly
    hourly.run(st.session_state.final_data, selected_level_1)

elif selected == "Weekday Analysis":
    import weekday
    weekday.run(st.session_state.final_data, selected_level_1)

elif selected == "Insights":
    import insights
    insights.run()
