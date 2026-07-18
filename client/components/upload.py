import streamlit as st
from utils.api import upload_pdfs_api

def render_uploader():
    st.sidebar.header("Upload Medical (.PDFs)")
    uploaded_files = st.sidebar.file_uploader("Upload multiple PDFs", type="pdf", accept_multiple_files=True)
    # if uploaded_files:
    #     response = upload_pdfs_api(uploaded_files)
    #     if response.status_code == 200:
    #         st.sidebar.success("Uploaded successfully")
    #     else:
    #         st.sidebar.error(f"Error : {response.text}")
    if "uploaded" not in st.session_state:
        st.session_state.uploaded = False

    if uploaded_files and not st.session_state.uploaded:
        with st.spinner("Uploading and creating vectors..."):
            response = upload_pdfs_api(uploaded_files)

        if response.status_code == 200:
            st.sidebar.success("Uploaded successfully")
            st.session_state.uploaded = True
        else:
            st.sidebar.error(f"Error: {response.text}")