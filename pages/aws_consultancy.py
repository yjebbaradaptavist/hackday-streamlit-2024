import streamlit as st
import pandas as pd

# Initialize connection.
conn = st.connection("snowflake")

df = conn.query("SELECT"
                    " SERVICE_ITEM,"
                    " SKU, "
                    " VARIANT_NAME, "
                    " DESCRIPTION_MARKETING,"
                    " SYNOPSIS_MARKETING,"
                    " TARGET_SIZE_OF_USERS,"
                    " TARGET_CUSTOMER,"
                    " STATUS,"
                    " RELATED_PRACTICES, "
                    " SERVICE_TYPE,"
                    " DELIVERY_LANGUAGES,"
                    " CONTRACT_TYPE,"
                    " DELIVERY_TEAMS,"
                    " DELIVERY_BUSINESS_UNIT"
                " FROM PROD_PREP.OUTPUT.VIEW_SERVICE_CATALOG_OUTPUT"
                " WHERE landing_metadata_file_name = ("
                "   SELECT MAX(landing_metadata_file_name)"
                "   FROM PROD_PREP.OUTPUT.VIEW_SERVICE_CATALOG_OUTPUT"
                " )"
                " AND SKU NOT IN ('') "
                " AND SERVICE_ITEM = 'AWS Consultancy'",
                ttl=600
)


service_item = df["SERVICE_ITEM"].to_list()[0]


st.title(f"{service_item} Service Details Page")

st.write(f"* :blue[**Service Item**]: {service_item}.")

sku = df["SKU"].to_list()[0]
st.write(f"* :blue[**SKU**]: {sku}.")

variant_name = df["VARIANT_NAME"].to_list()[0]
st.write(f"* :blue[**Variant Name**]: {variant_name}.")

description_marketing = df["DESCRIPTION_MARKETING"].to_list()[0]
st.write(f"* :blue[**Description**]: {description_marketing}")

synopsis_marketing = df["SYNOPSIS_MARKETING"].to_list()[0]
st.write(f"* :blue[**Synopsis Marketing**]:  {synopsis_marketing}.")

target_size_of_users = df["TARGET_SIZE_OF_USERS"].to_list()[0]
st.write(f"* :blue[**Target Size of Users**]:  {target_size_of_users}.")

target_customer = df["TARGET_CUSTOMER"].to_list()[0]
st.write(f"* :blue[**Target Customer**]:  {target_customer}.")

status = df["STATUS"].to_list()[0]
st.write(f"* :blue[**Status**]:  {status}.")

related_practices = df["RELATED_PRACTICES"].to_list()[0]
st.write(f"* :blue[**Related Practices**]:  {related_practices}.")

service_type = df["SERVICE_TYPE"].to_list()[0]
st.write(f"* :blue[**Service Type**]: {service_type}.")

contract_type = df["CONTRACT_TYPE"].to_list()[0]
st.write(f"* :blue[**Contract Type**]: {contract_type}.")

delivery_languages = df["DELIVERY_LANGUAGES"].to_list()[0]
st.write(f"* :blue[**Delivery Languages**]: {delivery_languages}.")

delivery_teams = df["DELIVERY_TEAMS"].to_list()[0]
st.write(f"* :blue[**Delivery Teams**]: {delivery_teams}.")

delivery_busines_unit = df["DELIVERY_BUSINESS_UNIT"].to_list()[0]
st.write(f"* :blue[**Delivery Business Unit**]: {delivery_busines_unit}.")

