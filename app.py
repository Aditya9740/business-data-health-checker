import pandas as pd
import streamlit as st

st.set_page_config(page_title="Business Data Health Checker", layout="wide")

st.title("📊 Business Data Health Checker")

st.markdown("Upload your business data and get instant insights on data quality and potential issues.")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📌 Data Preview")
    st.dataframe(df.head())

    st.subheader("📊 Summary")
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Rows", df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    col3.metric("Duplicate Rows", df.duplicated().sum())

    st.subheader("🧹 Data Issues")

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if not missing.empty:
        st.write("Missing Values:")
        st.dataframe(missing)
    else:
        st.success("No missing values found")

    st.subheader("💡 Recommendations")

    if df.duplicated().sum() > 0:
        st.warning("Remove duplicate rows to avoid incorrect reporting")

    if missing.sum() > 0:
        st.warning("Handle missing values to improve data accuracy")

    st.info("Standardize formats (dates, categories)")
    st.info("Validate business logic before analysis")

st.markdown("---")

st.subheader("🚀 Want deeper insights?")

st.write("I provide detailed business data audits, dashboards, and cost optimization analysis.")

st.write("📧 Email: mahajanaditya814@gmail.com")
st.write("🔗 LinkedIn: linkedin.com/in/aditya-mahajan-58b432266")
