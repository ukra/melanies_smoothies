# Import python packages
# Import python packages
import streamlit as st
import snowflake
import pandas as pd
import requests
import urllib.parse


st.title("Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
    )
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:',name_on_order)
#cnx = st.connection("snowflake")
cnx = st.connection("snowflake")
session = cnx.session()
webpage = 'https://my.smoothiefroot.com/api/fruit/all'
data = pd.read_json(webpage)
ingredients_list = st.multiselect('Choose up to 5 ingrdients:', data['name'], max_selections = 5)
if ingredients_list: #is not null:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        urlstring = 'my.smoothiefroot.com/api/fruit/' + fruit_chosen
        encoded_web_address = 'https://' + urllib.parse.quote(urlstring)
        smoothie_response = requests.get(encoded_web_address)
        count_df = pd.DataFrame(data=smoothie_response.json(), index=[0])
        if len(count_df.columns) > 5:
            df = pd.DataFrame(data=smoothie_response.json())
            if 'nutrition' in df.columns:
                transposed_df = df[['nutrition']].transpose()
                num_columns = len(transposed_df.columns)
                if num_columns == 4:
                    transposed_df.columns = ['Carbs', 'Fat', 'Protein', 'Sugar']
                    w = 400
                elif num_columns == 3:
                    transposed_df.columns = ['Carbs', 'Fat', 'Protein']
                    w = 300   
                st.dataframe(transposed_df,width=w,hide_index=True)
        else:
            st.write('No nutrition data found')
    my_insert_stmt = """insert into smoothies.public.orders(ingredients) 
                            values('""" + ingredients_string +""",""" + name_on_order +"""')"""
time_to_insert = st.button('Submit Order')
if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered, '+ name_on_order + '!', icon='✅')




