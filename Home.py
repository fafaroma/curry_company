import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon=''
)

#image_path = 'C:\\Users\\olive\\Downloads\\Curso\\Logo.png'
image = Image.open('Logo.png')
st.sidebar.image(image, width=120)


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write('# Curry Company Growth Dashboard')