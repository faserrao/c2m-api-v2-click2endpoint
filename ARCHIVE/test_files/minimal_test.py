import streamlit as st

st.title("Minimal Test")
st.write("If you can see this, Streamlit is working!")

if st.button("Click me"):
    st.write("Button clicked!")