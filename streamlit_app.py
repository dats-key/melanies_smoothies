# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# アプリのタイトルを記載
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothe!
    """
)

# 注文のタイトルを記載
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be:", name_on_order)

# fruit_optionsからFRUIT_NAME列をSELECT
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

# pandasを使用
pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

# マルチ選択ボックスを追加
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections = 5)

# マルチ選択ボックスに値が入ると以下処理を行う
if ingredients_list:

    # 変数を作成
    ingredients_string = ''

    # クエリ実行用の変数にフルーツ名を入れる
    for fruits_chosen in ingredients_list:
        ingredients_string += fruits_chosen + ' '

    # search_on列がある対象のみに絞るクエリを実行
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruits_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruits_chosen,' is ', search_on, '.')

    # 対象フルーツに対してfruityviceへREST API呼び出し
        st.subheader(fruits_chosen + 'Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    # st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    # st.write(my_insert_stmt)
    # st.stop()
    
    # Submitボタンを押下したらOrdersにInsertして、注文完了メッセージを表示
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success('Your Smoothie is ordered!' + name_on_order, icon="✅")

# ライブラリ`requests`でREST API呼び出しを送信
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
