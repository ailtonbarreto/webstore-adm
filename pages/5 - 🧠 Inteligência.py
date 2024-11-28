import streamlit as st
import streamlit.components.v1 as components





st.set_page_config(page_title="Inteligência", page_icon="📊", layout="wide",initial_sidebar_state="collapsed")

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)
    

components.iframe("./dashboard-webstore.html",width=1000)
    
