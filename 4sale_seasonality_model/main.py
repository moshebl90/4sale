import streamlit as st
import pandas as pd
import gdown
import os
from streamlit_option_menu import option_menu

# Set up the page
st.set_page_config(page_title="4sale Seasonality Analysis", page_icon=":bar_chart:", initial_sidebar_state="expanded")

# Sidebar image
st.sidebar.image("4sale_seasonality_model/images.png", use_container_width=True)

# Sidebar menu options
with st.sidebar:
    selected = option_menu(
        "Navigation",
        ["Info", "Monthly Analysis", "Weekly Analysis", "Daily Analysis",
         "Weekly in Month Analysis", "Hourly Analysis", "Weekday Analysis", "Insights"],
        icons=["info-circle", "calendar", "calendar-week", "calendar-day", "calendar-check", "clock", "calendar-event", "graph-up-arrow"],
        menu_icon="cast",
        default_index=0,
    )

# Sidebar filters (conditionally rendered after data is loaded)
if "final_data" in st.session_state:
    level_1_options = st.session_state.final_data["Level-1"].unique()
    selected_level_1 = st.sidebar.selectbox("Select Level-1 Category", options=["All"] + list(level_1_options))
else:
    st.sidebar.warning("Data is being processed from Google Drive, please wait.")

# Check if data exists in session state
if 'final_data' not in st.session_state:
    # Google Drive file links
    transactions_url = "https://drive.google.com/file/d/14h_94INBkzAxLqopeNbZOCVkWMQktAAb/view?usp=sharing"
    listings_url = "https://docs.google.com/spreadsheets/d/17hpoGgMX15s_EkOsJfEjUkoyZWesOSGq_MUlyhiFfjE/edit?usp=sharing"

    # Download files from Google Drive
    gdown.download(transactions_url, "transactions.csv", quiet=False)
    gdown.download(listings_url, "listingsCategories.xlsx", quiet=False)

    # Check if files are downloaded successfully
    if not os.path.exists("transactions.csv") or not os.path.exists("listingsCategories.xlsx"):
        st.error("Files could not be downloaded. Please check the file URLs or your internet connection.")
    else:
        try:
            # Try reading the CSV with different delimiters
            transactions = pd.read_csv("transactions.csv", encoding='utf-8', delimiter=',', on_bad_lines='skip')
            # If the above doesn't work, try tab or semicolon delimiters
            if transactions.empty:
                transactions = pd.read_csv("transactions.csv", encoding='utf-8', delimiter=';', on_bad_lines='skip')
                if transactions.empty:
                    transactions = pd.read_csv("transactions.csv", encoding='utf-8', delimiter='\t', on_bad_lines='skip')

            # Ensure the listings file is valid and has the correct format
            if listings_url.endswith('.xlsx'):
                # Read the Excel file with specified engine
                listings = pd.read_excel("listingsCategories.xlsx", engine='openpyxl')  # Specify engine for .xlsx files
            else:
                raise ValueError("The listings file is not an Excel (.xlsx) file.")

            # Data cleaning and merging
            listings["Level-1"] = listings["FULL_PATH"].str.split(" --_-- ").str[0]
            transactions = transactions.rename(columns={"CATEGORY_ID": "CAT_ID"})
            final_data = transactions.merge(listings[["CAT_ID", "Level-1"]], on="CAT_ID", how="left")

            # Save final_data to session state
            st.session_state.final_data = final_data

            # Success message after processing data
            st.success("Data loaded from Google Drive and processed successfully! You can now proceed to analysis.")
        except Exception as e:
            st.error(f"Error reading the files: {e}")
            st.stop()

# Navigation options
if selected == "Info":
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
    insights.run(st.session_state.final_data)
