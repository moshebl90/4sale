import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# Set up the page
st.set_page_config(page_title="4sale Seasonality Analysis", page_icon=":bar_chart:", initial_sidebar_state="expanded")

# Sidebar image
st.sidebar.image("images.png", use_container_width=True)

# Sidebar menu options
with st.sidebar:
    selected = option_menu(
        "Navigation",
        ["Upload Data", "Info", "Monthly Analysis", "Weekly Analysis", "Daily Analysis",
         "Weekly in Month Analysis", "Hourly Analysis","Weekday Analysis","Insights"],
        icons=["cloud-upload", "info-circle", "calendar", "calendar-week", "calendar-day", "calendar-check", "clock","calendar-event","graph-up-arrow"],
        menu_icon="cast",
        default_index=0,
    )

# Sidebar filters
st.sidebar.title("Filters")

# Handle file uploads
transactions_file = st.file_uploader("Upload Transactions.csv", type=["csv"])
listings_file = st.file_uploader("Upload ListingsCategories.csv", type=["csv"])

# If files are uploaded, process them
if transactions_file and listings_file:
    transactions = pd.read_csv(transactions_file)
    listings = pd.read_csv(listings_file)

    # Data cleaning and merging
    listings["Level-1"] = listings["FULL_PATH"].str.split(" --_-- ").str[0]
    transactions = transactions.rename(columns={"CATEGORY_ID": "CAT_ID"})
    final_data = transactions.merge(listings[["CAT_ID", "Level-1"]], on="CAT_ID", how="left")

    # Store the data in session state or a temporary file if needed for later analysis
    st.session_state.final_data = final_data

    # Display success message
    st.success("Data uploaded and processed successfully! You can now proceed to analysis.")

else:
    # Load pre-existing final_data if not uploaded (Optional: Add a fallback for Streamlit Cloud)
    if 'final_data' in st.session_state:
        final_data = st.session_state.final_data
    else:
        st.warning("Please upload the data files to proceed.")

# Level-1 filter options based on the uploaded data
if 'final_data' in locals():
    level_1_options = final_data["Level-1"].unique()
    selected_level_1 = st.sidebar.selectbox("Select Level-1 Category", options=["All"] + list(level_1_options))

# Different analysis sections based on selected option
if selected == "Upload Data":
    st.header("Upload Data Files")
    # Additional file upload logic can go here
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
elif selected == "Weekday Analysis":
    import weekday
    weekday.run(selected_level_1)
elif selected == "Insights":
    import insights
    insights.run()
