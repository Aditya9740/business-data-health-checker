import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Business Data Health Checker", layout="wide")

st.title("📊 Business Data Health Checker")
st.info("🔍 This is a quick automated check. For deeper insights, I provide detailed business analysis and dashboards.")
st.markdown("Upload your business data and get instant insights on data quality, reporting risks, and business patterns.")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

def load_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    return None

def find_numeric_columns(df):
    return df.select_dtypes(include="number").columns.tolist()

def build_summary_text(
    file_name,
    rows,
    cols,
    duplicates,
    missing_df,
    negative_df,
    numeric_summary,
):
    lines = []
    lines.append("Business Data Health Checker - Summary Report")
    lines.append("=" * 50)
    lines.append(f"File: {file_name}")
    lines.append(f"Total Rows: {rows}")
    lines.append(f"Total Columns: {cols}")
    lines.append(f"Duplicate Rows: {duplicates}")
    lines.append("")

    lines.append("Missing Values")
    lines.append("-" * 20)
    if not missing_df.empty:
        lines.append(missing_df.to_string(index=False))
    else:
        lines.append("No missing values found.")
    lines.append("")

    lines.append("Negative Value Detection")
    lines.append("-" * 20)
    if not negative_df.empty:
        lines.append(negative_df.to_string(index=False))
    else:
        lines.append("No negative numeric values found.")
    lines.append("")

    lines.append("Top-Level KPI Totals")
    lines.append("-" * 20)
    if numeric_summary:
        for col, value in numeric_summary.items():
            lines.append(f"{col}: {value:,.2f}")
    else:
        lines.append("No numeric columns available for KPI totals.")
    lines.append("")

    lines.append("Recommendations")
    lines.append("-" * 20)
    if duplicates > 0:
        lines.append("- Remove duplicate rows to avoid incorrect reporting.")
    if not missing_df.empty:
        lines.append("- Handle missing values before dashboarding or business analysis.")
    if not negative_df.empty:
        lines.append("- Review negative values to confirm whether they are valid returns, credits, refunds, or data errors.")
    lines.append("- Standardize dates, categories, and text labels.")
    lines.append("- Validate business logic before final reporting.")

    return "\n".join(lines)

if uploaded_file is not None:
    df = load_file(uploaded_file)

    if df is None:
        st.error("Unsupported file type.")
    else:
        st.subheader("📌 Data Preview")
        st.table(df.head(10))

        st.subheader("📊 Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", df.shape[0])
        col2.metric("Total Columns", df.shape[1])
        col3.metric("Duplicate Rows", int(df.duplicated().sum()))

        st.subheader("🧹 Data Issues")

        # Missing values
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
            missing_df = pd.DataFrame()
            st.success("No missing values found.")

        # Negative value detection
        st.subheader("⚠ Negative Value Detection")
        numeric_cols = find_numeric_columns(df)
        negative_records = []

        for col in numeric_cols:
            neg_count = int((df[col] < 0).sum())
            if neg_count > 0:
                negative_records.append({
                    "Column": col,
                    "Negative Values": neg_count
                })

        if negative_records:
            negative_df = pd.DataFrame(negative_records)
            st.table(negative_df)
        else:
            negative_df = pd.DataFrame()
            st.success("No negative numeric values found.")

        # KPI totals
        st.subheader("💰 Top-Level KPI Totals")
        numeric_summary = {}
        if numeric_cols:
            for col in numeric_cols[:6]:
                numeric_summary[col] = float(df[col].sum())
            kpi_cols = st.columns(min(len(numeric_summary), 3) if len(numeric_summary) > 0 else 1)

            idx = 0
            for col_name, total_value in numeric_summary.items():
                kpi_cols[idx % len(kpi_cols)].metric(f"Total {col_name}", f"{total_value:,.2f}")
                idx += 1
        else:
            st.info("No numeric columns available for KPI totals.")

        # Charts
        st.subheader("📈 Basic Charts")
        if numeric_cols:
            selected_chart_col = st.selectbox("Select numeric column for chart", numeric_cols)
            chart_type = st.radio("Select chart type", ["Bar Chart", "Line Chart"], horizontal=True)

            value_counts_df = (
                df[selected_chart_col]
                .value_counts(dropna=False)
                .reset_index()
            )
            value_counts_df.columns = [selected_chart_col, "Count"]

            if chart_type == "Bar Chart":
                st.bar_chart(value_counts_df.set_index(selected_chart_col)["Count"])
            else:
                line_df = df[[selected_chart_col]].copy()
                st.line_chart(line_df)
        else:
            st.info("No numeric columns available for charting.")

        # Column types
        st.subheader("📋 Column Types")
        dtype_df = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values
        })
        st.table(dtype_df)

        # Recommendations
        st.subheader("💡 Recommendations")
        issues_found = False

        if df.duplicated().sum() > 0:
            st.warning("Remove duplicate rows to avoid incorrect reporting.")
            issues_found = True

        if not missing_df.empty:
            st.warning("Handle missing values to improve data accuracy.")
            issues_found = True

        if not negative_df.empty:
            st.warning("Review negative values to confirm whether they are valid credits/refunds or data issues.")
            issues_found = True

        st.info("Standardize formats such as dates, categories, and text values.")
        st.info("Validate business logic before doing final reporting or dashboarding.")

        if not issues_found:
            st.success("Your dataset looks clean at a basic level. You can move to deeper business analysis.")

        # Downloadable report
        st.subheader("📄 Download Summary Report")
        report_text = build_summary_text(
            file_name=uploaded_file.name,
            rows=df.shape[0],
            cols=df.shape[1],
            duplicates=int(df.duplicated().sum()),
            missing_df=missing_df,
            negative_df=negative_df,
            numeric_summary=numeric_summary,
        )

        st.download_button(
            label="Download Report (.txt)",
            data=report_text,
            file_name="business_data_health_report.txt",
            mime="text/plain"
        )

st.markdown("---")
st.subheader("🚀 Want deeper insights?")
st.write("I provide detailed business data audits, dashboards, and cost optimization analysis.")
st.write("📧 Email: mahajanaditya814@gmail.com")
st.write("🔗 LinkedIn: linkedin.com/in/aditya-mahajan-58b432266")
