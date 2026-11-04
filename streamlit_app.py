
# This app is designed to demonstrate how to create a user interface for accepting user input, reading in data, and writing back data to Snowflake!

# Import python packages
import streamlit as st
import os
from snowflake.snowpark.functions import col
from snowflake.snowpark.functions import col, when_matched
import requests
import pandas as pd

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw: ")
st.write(
  """ Choose the fruits you want in your custom Smoothie!

  """
)

name_on_order = st.text_input('Name On Smoothie:')
st.write('The name on your Smoothie will be: ', name_on_order)

#session = get_active_session()
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

# Convert the snowpark dataframe to pandas dataframe so that we can use the LOC function 
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect('Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
)

# Changing the LIST to a STRING. To convert a LIST to a STRING, we first need to create a variable and make sure Python treats it # as a string. # We do this by setting the variable to an empty string:
# IMPORTANT: # DO NOT put a space between the quotes. It may look like there is a space, but there must not be one.
# Create the INGREDIENTS_STRING Variable

if ingredients_list:
    ingredients_string = ''

# How a FOR LOOP Block Works-We can use the phrase:  
# for fruit_chosen in ingredients_list: # which actually means...  
# for each fruit_chosen in ingredients_list multiselect box: do everything below this line that # is indented.
# We never defined a variable named fruit_chosen, but Python understands that whatever is placed  in that position is a counter for items in the list.
# So we could just as easily say: for x in ingredients_list:  OR 
# for each_fruit in ingredients_list:# Add the For Block. The += operator means "add this to what is already in the variable" so each # time the FOR Loop is repeated, a new fruit name is appended to the existing string.

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen +  ' '
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]  
        # st.write('The search value for', fruit_chosen, 'is', search_on, ',' )
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df=st.dataframe(data=smoothiefroot_response.json(), use_container_width = True)
        
        st.subheader(fruit_chosen + 'Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit" + fruit_chosen)
      
my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
        values ('""" + ingredients_string + """','""" + name_on_order + """')"""
st.write(my_insert_stmt)

time_to_insert = st.button('Submit Order')
if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")

st.subheader("Pending Orders")

# Fetch orders from Snowflake where ORDER_FILLED is false/0
pending_orders_df = session.table("smoothies.public.orders").filter(col("ORDER_FILLED") == 0)
# Convert Snowpark dataframe to pandas for st.data_editor
editable_df = pending_orders_df.to_pandas() 
  
# Display the data editor with checkboxes for ORDER_FILLED
if not editable_df.empty:
    edited_dataset = st.data_editor(editable_df, key="pending_orders_editor")

    submitted = st.button('Submit')

    if submitted:
        try:
            # Create a Snowpark dataframe from the edited pandas dataframe
            og_dataset = session.create_dataframe(edited_dataset)
            
            # Update the Snowflake table where order IDs match
            session.table("smoothies.public.orders").merge(
                og_dataset,
                (session.table("smoothies.public.orders")['ORDER_UID'] == og_dataset['ORDER_UID']),
                [when_matched().update({'ORDER_FILLED': og_dataset['ORDER_FILLED']})]
            )
            st.success("Order(s) updated successfully!", icon="👍")
            st.rerun()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
else:
    st.success("There are no pending orders right now! 🎉", icon="☕")

    

    
