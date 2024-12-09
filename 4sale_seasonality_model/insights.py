import streamlit as st
import pandas as pd
from info import calculate_yearly_totals

def run(final_data):
    st.title("Business Insights & Recommendations")

    st.subheader("Introduction")
    st.write("""
       TBC
    """)

    st.subheader("Challenges")
    st.write("""
    Based on below yearly Data 2023 data is totally missed with a clear decrease in 2022 Transactions 
        """)
    yearly_totals = calculate_yearly_totals(final_data, 'TIMESTAMP')
    st.dataframe(yearly_totals)

    st.write("""
       From The above table we can see around 90% increase in 2024 Transaction compare to 2022 
       We can't ignore the missing data for 2023 but will share the growth in % based on the given data on the attached slides 
                 """)


