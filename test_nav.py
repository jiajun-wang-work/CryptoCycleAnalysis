import streamlit as st

st.set_page_config(layout="wide")

# Initialize session state
if 'counter' not in st.session_state:
    st.session_state['counter'] = 0

if 'lang' not in st.session_state:
    st.session_state['lang'] = 'en'

# Read query params
params = st.query_params
if "lang" in params:
    st.session_state['lang'] = params["lang"]

st.write(f"Current Lang: {st.session_state['lang']}")
st.write(f"Counter: {st.session_state['counter']}")

if st.button("Increment"):
    st.session_state['counter'] += 1

# Custom Nav
st.markdown("""
<div style="position: fixed; top: 10px; right: 10px; z-index: 1000;">
    <a href="?lang=en" target="_self"><button>EN</button></a>
    <a href="?lang=cn" target="_self"><button>CN</button></a>
</div>
""", unsafe_allow_html=True)
