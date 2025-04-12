
import streamlit as st

st.title("Test legenda HTML")

col1, col2 = st.columns([3, 1])

with col1:
    st.write("Contenuto a sinistra...")


        with col_legenda:
            st.markdown("""
                <span style='color:green'><b>Verde</b></span>: Estratti base<br>
                <span style='color:orange'><b>Arancione</b></span>: Precedenti/Successivi<br>
                <span style='color:red; font-size:18px'><b>A</b></span>: Ambo<br>
                <span style='color:red; font-size:18px'><b>T</b></span>: Terno
            """, unsafe_allow_html=True)

