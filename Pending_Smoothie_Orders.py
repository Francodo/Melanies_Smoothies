# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import os
from snowflake.snowpark.functions import col, when_matched
import pandas as pd

# Write directly to the app

st.title(f":cup_with_straw: Pending Smoothie Orders:cup_with_straw: ")
st.write(""" Orders that will need to be filled.
           """
)

# session = get_active_session()
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.orders").filter(col('ORDER_FILLED'))

if my_dataframe:
    editable_df = st.data_editor(my_dataframe)
    submitted = st.button('Submit')

    if submitted:
#    st.success("Someone clicked the button.", icon = "👍")
 
            # 1. Grab the original table
                og_dataset = session.table("smoothies.public.orders")
            
            # 2. Convert the edited pandas dataframe back into a Snowpark dataframe
                edited_dataset = session.create_dataframe(editable_df)
            
        # 3. Perform the merge to update ORDER_FILLED in Snowflake
                try:    
                    og_dataset.merge(
                    edited_dataset,
                    (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID']),
                    [when_matched().update({'ORDER_FILLED':       edited_dataset['ORDER_FILLED']})]
            )
                    st.success("Orders updated successfully!", icon="👍")
            
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
                    
    else:
        st.success("There are no pending orders right now! 🎉", icon="☕")
