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
    transactions_url = "https://drive.google.com/uc?id=14h_94INBkzAxLqopeNbZOCVkWMQktAAb"
    listings_url = "https://docs.google.com/spreadsheets/d/165EmqELxzDlWrCjGE-yjxd-SlkMmHx9VdWBFrn3T78s/export?format=csv&id=165EmqELxzDlWrCjGE-yjxd-SlkMmHx9VdWBFrn3T78s"

    # Download files from Google Drive
    gdown.download(transactions_url, "transactions.csv", quiet=False)
    gdown.download(listings_url, "listingsCategories.csv", quiet=False)

    # Check if files are downloaded successfully
if os.path.exists("transactions.csv"):
    try:
        # Read the CSV file for transactions in chunks
        chunksize = 10000  # Adjust chunk size based on your needs
        for chunk in pd.read_csv("transactions.csv", encoding='utf-8', chunksize=chunksize, header=0, on_bad_lines='skip', delimiter=',', quotechar='"'):
            # Clean and process the chunk
            chunk.columns = chunk.columns.str.strip()  # Strip any leading/trailing whitespace from columns
            if "CATEGORY_ID" not in chunk.columns:
                st.error("'CATEGORY_ID' column not found in transactions file.")
                st.stop()

            # Rename CATEGORY_ID to CAT_ID
            chunk = chunk.rename(columns={"CATEGORY_ID": "CAT_ID"})

            # Process listings data
            listings = pd.read_csv("listingsCategories.csv", encoding='utf-8', delimiter=',', quotechar='"', on_bad_lines='skip')

            # Check columns in listings file to ensure FULL_PATH exists
            if "FULL_PATH" not in listings.columns:
                st.error("'FULL_PATH' column not found in listings file.")
                st.stop()

            # Extract 'Level-1' from 'FULL_PATH' in listings file
            listings["Level-1"] = listings["FULL_PATH"].str.split(" --_-- ").str[0]

            # Merge the chunk with the listings data on 'CAT_ID'
            chunk = chunk.merge(listings[["CAT_ID", "Level-1"]], on="CAT_ID", how="left")

            # Append the chunk to the final data
            if 'final_data' not in locals():
                final_data = chunk
            else:
                final_data = pd.concat([final_data, chunk], ignore_index=True)

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
