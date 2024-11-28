import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Inteligência", page_icon="📊", layout="wide",initial_sidebar_state="collapsed")



components.iframe("dashboard-webstore.html",height=1000)
    
