import pandas as pd
import streamlit as st

st.set_page_config(page_title="Business Data Health Checker", layout="wide")

st.title("📊 Business Data Health Checker")
st.info("🔍 This is a quick automated check. For deeper insights, I provide detailed business analysis and dashboards.")

st.markdown("Upload your business data and get instant insights on data quality and potential issues.")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📌 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("📊 Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    col3.metric("Duplicate Rows", int(df.duplicated().sum()))

    st.subheader("🧹 Data Issues")

    missing = df.isnull().sum()
    missing = missing[missing > 0]

missing = df.isnull().sum()
missing = missing[missing > 0]

if not missing.empty:
    missing_df = pd.DataFrame({
        "Column": missing.index.tolist(),
        "Missing Values": missing.values.tolist(),
        "Missing %": ((missing.values / len(df)) * 100).round(2).tolist()
    })

    st.write(f"Columns with missing values: {len(missing_df)}")
    st.write(f"Total missing cells: {int(missing.sum())}")
    st.table(missing_df)
else:
    st.success("No missing values found.")

    st.subheader("📋 Column Types")
    dtype_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values
    })
    st.dataframe(dtype_df, use_container_width=True)

    st.subheader("💡 Recommendations")

    issues_found = False

    if df.duplicated().sum() > 0:
        st.warning("Remove duplicate rows to avoid incorrect reporting.")
        issues_found = True

    if not missing.empty:
        st.warning("Handle missing values to improve data accuracy.")
        issues_found = True

    st.info("Standardize formats such as dates, categories, and text values.")
    st.info("Validate business logic before doing final reporting or dashboarding.")

    if not issues_found:
        st.success("Your dataset looks clean at a basic level. You can move to deeper business analysis.")

st.markdown("---")
st.subheader("🚀 Want deeper insights?")
st.write("I provide detailed business data audits, dashboards, and cost optimization analysis.")
st.write("📧 Email: mahajanaditya814@gmail.com")
st.write("🔗 LinkedIn: linkedin.com/in/aditya-mahajan-58b432266")
