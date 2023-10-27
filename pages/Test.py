import json

import streamlit as st

DOWNLOADS_DIRECTORY = 'downloads/'

st.write("We are in test")

with open(DOWNLOADS_DIRECTORY + 'test.json') as outfile:
    abc = json.load(outfile)

st.json(abc)

st.dataframe(abc['aaData'])

