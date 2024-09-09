# streamlit_app.py

import streamlit as st
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd

# Page layout
## Page expands to full width
st.write("pageholder 4 clickthrough ")