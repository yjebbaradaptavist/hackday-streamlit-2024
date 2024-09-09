# streamlit_app.py

import streamlit as st
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
import time
import numpy as np


# Page layout
## Page expands to full width
st.set_page_config(
    page_title="Service Catalog App",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)
#---------------------------------#
# Page layout (continued)
## Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
col1 = st.sidebar
col2, col3 = st.columns((2,1))
# Sidebar + Main panel
col1.header('Filters Options')


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = col1.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()


    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = col1.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df
# Initialize connection.
conn = st.connection("snowflake")

# Perform query.
df = conn.query("SELECT "
                    " SKU,"
                    " TARGET_SIZE_OF_USERS,"
                    " TARGET_CUSTOMER,"
                    " SYNOPSIS_MARKETING,"
                    " STATUS,"
                    " SERVICE_TYPE,"
                    " DELIVERY_LANGUAGES,"
                    " DELIVERY_BUSINESS_UNIT"
                " FROM PROD_PREP.OUTPUT.VIEW_SERVICE_CATALOG_OUTPUT"
                " WHERE landing_metadata_file_name = ("
                "   SELECT MAX(landing_metadata_file_name)"
                "   FROM PROD_PREP.OUTPUT.VIEW_SERVICE_CATALOG_OUTPUT"
                " )"
                " AND SKU NOT IN ('')",
                ttl=600
)

select, details = st.tabs(["Select SKUs", "See details of selected"])

with select: # Add select tab #############################################
    st.title("Auto Filter Dataframes in Streamlit")
    st.header("\n Select filters on the sidebar to get to information that you need \n ")
    filtered_df = filter_dataframe(df)
    filtered_df.rename(columns=lambda name: name.replace('_', ' ').title(), inplace=True)
    styled_df = filtered_df.style.map(lambda x: f"background-color: {'green' if x=='Live' else 'yellow'}", subset='Status')

    #def dataframe_with_selections(df):
    #    df_with_selections = df.copy()
    #    df_with_selections.insert(0, "Select", False)
    #    edited_df = st.data_editor(
    #        df_with_selections,
    #        hide_index=True,
    #        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
    #        disabled=df.columns,
    #    )
    #    selected_indices = list(np.where(edited_df.Select)[0])
    #    #selected_rows = df[edited_df.Select]
    #    return {"selected_rows_indices": selected_indices}#, "selected_rows": selected_rows}


    #selection = dataframe_with_selections(filtered_df)
    #st.write("Your selection:")
    #st.write(selection)

    event = st.dataframe(styled_df, hide_index=True,selection_mode="multi-row",use_container_width=True,on_select="rerun")

    st.header("Selected SKU")
    sku = event.selection.rows
    selected_df = filtered_df.iloc[sku]
    st.dataframe(
            selected_df,
            use_container_width=True,
        )

    
with details: # Add compare tab ###########################################
    col4, col5 = st.columns((2,1))
    selected_df = filtered_df.iloc[sku]["Synopsis Marketing"]
    col4.dataframe(selected_df,use_container_width=True)

    selected_df = filtered_df.iloc[sku]["Target Size Of Users"]
    col4.dataframe(selected_df,use_container_width=True)

    selected_df = filtered_df.iloc[sku]["Delivery Languages"]
    col5.dataframe(selected_df,use_container_width=True)

    selected_df = filtered_df.iloc[sku]["Delivery Business Unit"]
    col5.dataframe(selected_df,use_container_width=True)
    

    st.header("A chart to prove the point")
    last_rows = np.random.randn(1, 1)
    chart = st.line_chart(last_rows)
    for i in range(1, 101):
        new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
        chart.add_rows(new_rows)
        last_rows = new_rows
        time.sleep(0.05)
    

    # Streamlit widgets automatically run the script from top to bottom. Since
    # this button is not connected to any other logic, it just causes a plain
    # rerun.
    st.button("Re-run")

    st.write(filtered_df.columns)    

#Sku
#Target Size Of Users
#Target Customer
#Synopsis Marketing
#Status
#Service Type
#Delivery Languages
#Delivery Business Unit