import streamlit as st

st.set_page_config(page_title="Button Test")

st.title("Testing Button Selection")

# Test 1: Simple button selection
st.header("Test 1: Simple Buttons")
if "test1_selected" not in st.session_state:
    st.session_state.test1_selected = None

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Option A", key="btn_a"):
        st.session_state.test1_selected = "A"
with col2:
    if st.button("Option B", key="btn_b"):
        st.session_state.test1_selected = "B"
with col3:
    if st.button("Option C", key="btn_c"):
        st.session_state.test1_selected = "C"

st.write(f"Selected: {st.session_state.test1_selected}")

# Test 2: Button with rerun
st.header("Test 2: Button with Rerun")
if "test2_selected" not in st.session_state:
    st.session_state.test2_selected = None

if st.button("Click me and rerun", key="rerun_btn"):
    st.session_state.test2_selected = "Clicked"
    st.rerun()

st.write(f"Test 2 State: {st.session_state.test2_selected}")

# Test 3: Dynamic buttons like in the app
st.header("Test 3: Dynamic Question Flow")
if "answers" not in st.session_state:
    st.session_state.answers = {}

# Question 1
if "q1" not in st.session_state.answers:
    st.subheader("Question 1: Pick a color")
    cols = st.columns(3)
    for i, color in enumerate(["Red", "Green", "Blue"]):
        with cols[i]:
            if st.button(color, key=f"color_{color}"):
                st.session_state.answers["q1"] = color
                st.rerun()
else:
    st.write(f"Q1 Answer: {st.session_state.answers['q1']}")
    
    # Question 2 (only shows after Q1)
    if "q2" not in st.session_state.answers:
        st.subheader("Question 2: Pick a size")
        cols = st.columns(3)
        for i, size in enumerate(["Small", "Medium", "Large"]):
            with cols[i]:
                if st.button(size, key=f"size_{size}"):
                    st.session_state.answers["q2"] = size
                    st.rerun()
    else:
        st.write(f"Q2 Answer: {st.session_state.answers['q2']}")

# Show all state
with st.expander("Full Session State"):
    st.json(dict(st.session_state))
    
if st.button("Reset All", key="reset"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()