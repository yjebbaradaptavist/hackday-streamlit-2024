# streamlit_app.py

import streamlit as st
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
from streamlit_extras.stylable_container import stylable_container



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
df = conn.query("SELECT"
                    " SERVICE_ITEM,"
                    " SKU, "
                    " VARIANT_NAME, "
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

st.title("Service Catalog Streamlit App")
filtered_df = filter_dataframe(df)

variant_name_list = filtered_df['VARIANT_NAME'].tolist()

service_item_list = filtered_df['SERVICE_ITEM'].tolist()

if 'pages' not in st.session_state:
    st.session_state['pages'] = './pages'
for i in range(0,len(service_item_list)):
    variant_name = "" if variant_name_list[i] == "-" else variant_name_list[i]
    service_item = service_item_list[i]
    label_name = service_item if variant_name == "" else f"{service_item} {variant_name}"
    with stylable_container(
    "green",
    css_styles="""
    button {
        background-color: black;
        color: white;
    }"""
    ):
        is_clicked = st.button(label=label_name,
                  key=f"{service_item}{variant_name}{i}",
                  use_container_width=True,
                  
        )
        if is_clicked:
            formatted_label_name = label_name.replace(" ","_").lower()
            st.switch_page(f"./pages/{formatted_label_name}.py")
        

