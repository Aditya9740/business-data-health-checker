import pandas as pd
import streamlit as st

st.set_page_config(page_title="Business Data Health Checker", layout="wide")

st.title("📊 Business Data Health Checker")
st.info("🔍 This is a quick automated check. For deeper insights, I provide detailed business analysis and dashboards.")
st.markdown("Upload your business data and get instant insights on data quality, reporting risks, and business patterns.")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

# ---------- HELPERS ----------

def load_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    return None

def clean_numeric_series(series):
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.strip()
        .replace(["", "nan", "None"], pd.NA)
    )
    return pd.to_numeric(cleaned, errors="coerce")

def detect_numeric_like_columns(df):
    numeric_like_cols = []
    for col in df.columns:
        if df[col].dtype == "object":
            sample = df[col].dropna().astype(str).head(20)
            if not sample.empty:
                converted = pd.to_numeric(
                    sample.str.replace(",", "", regex=False).str.replace("₹", "", regex=False),
                    errors="coerce"
                )
                if converted.notna().mean() >= 0.6:
                    numeric_like_cols.append(col)
    return numeric_like_cols

def standardize_text(series):
    return series.astype(str).str.strip().str.lower()

def build_summary_text(
    file_name,
    rows,
    cols,
    duplicates,
    missing_df,
    negative_df,
    numeric_summary,
    invalid_date_summary,
    standardized_text_cols
):
    lines = []
    lines.append("Business Data Health Checker - Client Audit Report")
    lines.append("=" * 55)
    lines.append(f"File: {file_name}")
    lines.append(f"Total Rows: {rows}")
    lines.append(f"Total Columns: {cols}")
    lines.append(f"Duplicate Rows: {duplicates}")
    lines.append("")

    lines.append("Missing Values")
    lines.append("-" * 25)
    if not missing_df.empty:
        lines.append(missing_df.to_string(index=False))
    else:
        lines.append("No missing values found.")
    lines.append("")

    lines.append("Negative Value Detection")
    lines.append("-" * 25)
    if not negative_df.empty:
        lines.append(negative_df.to_string(index=False))
    else:
        lines.append("No negative numeric values found.")
    lines.append("")

    lines.append("Date Validation")
    lines.append("-" * 25)
    if invalid_date_summary:
        for col, count in invalid_date_summary.items():
            lines.append(f"{col}: {count} invalid dates")
    else:
        lines.append("No invalid date issues found.")
    lines.append("")

    lines.append("Standardized Text Columns")
    lines.append("-" * 25)
    if standardized_text_cols:
        for col in standardized_text_cols:
            lines.append(f"- {col}")
    else:
        lines.append("No text standardization applied.")
    lines.append("")

    lines.append("Top-Level KPI Totals")
    lines.append("-" * 25)
    if numeric_summary:
        for col, value in numeric_summary.items():
            lines.append(f"{col}: {value:,.2f}")
    else:
        lines.append("No numeric columns available for KPI totals.")
    lines.append("")

    lines.append("Recommendations")
    lines.append("-" * 25)
    if duplicates > 0:
        lines.append("- Remove duplicate rows to avoid incorrect reporting.")
    if not missing_df.empty:
        lines.append("- Handle missing values before dashboarding or business analysis.")
    if not negative_df.empty:
        lines.append("- Review negative values to confirm whether they are valid credits/refunds or data errors.")
    if invalid_date_summary:
        lines.append("- Fix invalid date formats before time-based analysis.")
    if standardized_text_cols:
        lines.append("- Use standardized category/department/vendor labels for cleaner reporting.")
    lines.append("- Validate business logic before final reporting.")
    lines.append("- Build dashboards only after cleaning and standardization.")

    return "\n".join(lines)

# ---------- MAIN APP ----------

if uploaded_file is not None:
    df = load_file(uploaded_file)

    if df is None:
        st.error("Unsupported file type.")
    else:
        original_df = df.copy()

        st.subheader("📌 Data Preview")
        st.table(df.head(10))

        # -------- AUTO CLEAN NUMERIC-LIKE COLUMNS --------
        st.subheader("🛠 Auto Cleaning")
        numeric_like_cols = detect_numeric_like_columns(df)
        cleaned_numeric_cols = []

        for col in numeric_like_cols:
            cleaned_col = clean_numeric_series(df[col])
            # only replace if it meaningfully converts
            if cleaned_col.notna().sum() > 0:
                df[col] = cleaned_col
                cleaned_numeric_cols.append(col)

        if cleaned_numeric_cols:
            st.success(f"Converted to numeric: {', '.join(cleaned_numeric_cols)}")
        else:
            st.info("No messy numeric-like columns needed conversion.")

        # -------- DATE VALIDATION --------
        date_cols = [col for col in df.columns if "date" in col.lower()]
        invalid_date_summary = {}

        if date_cols:
            st.subheader("📅 Date Validation")
            for col in date_cols:
                parsed = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
                invalid_dates = df[col].notna().sum() - parsed.notna().sum()
                if invalid_dates > 0:
                    invalid_date_summary[col] = int(invalid_dates)
            if invalid_date_summary:
                invalid_date_df = pd.DataFrame({
                    "Column": list(invalid_date_summary.keys()),
                    "Invalid Dates": list(invalid_date_summary.values())
                })
                st.table(invalid_date_df)
            else:
                st.success("No invalid date issues found.")
        else:
            st.info("No date-like columns detected.")

        # -------- TEXT STANDARDIZATION --------
        st.subheader("🔤 Text Standardization")
        text_cols = df.select_dtypes(include="object").columns.tolist()
        likely_category_cols = [
            col for col in text_cols
            if any(word in col.lower() for word in ["department", "category", "vendor", "region"])
        ]

        standardized_text_cols = []
        for col in likely_category_cols:
            df[col] = standardize_text(df[col])
            standardized_text_cols.append(col)

        if standardized_text_cols:
            st.success(f"Standardized text labels in: {', '.join(standardized_text_cols)}")
        else:
            st.info("No category-like text columns detected for standardization.")

        # -------- SUMMARY --------
        st.subheader("📊 Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", df.shape[0])
        col2.metric("Total Columns", df.shape[1])
        col3.metric("Duplicate Rows", int(df.duplicated().sum()))

        # -------- DATA ISSUES --------
        st.subheader("🧹 Data Issues")
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

        # -------- NEGATIVE VALUE DETECTION --------
        st.subheader("⚠ Negative Value Detection")
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
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

        # -------- KPI TOTALS --------
        st.subheader("💰 Top-Level KPI Totals")
        numeric_summary = {}
        if numeric_cols:
            for col in numeric_cols[:6]:
                numeric_summary[col] = float(df[col].sum(skipna=True))

            kpi_cols = st.columns(min(len(numeric_summary), 3) if len(numeric_summary) > 0 else 1)
            idx = 0
            for col_name, total_value in numeric_summary.items():
                kpi_cols[idx % len(kpi_cols)].metric(f"Total {col_name}", f"{total_value:,.2f}")
                idx += 1
        else:
            st.info("No numeric columns available for KPI totals.")

        # -------- BASIC CHARTS --------
        st.subheader("📈 Basic Charts")
        if numeric_cols:
            selected_chart_col = st.selectbox("Select numeric column for chart", numeric_cols)
            chart_type = st.radio("Select chart type", ["Bar Chart", "Line Chart"], horizontal=True)

            if chart_type == "Bar Chart":
                chart_df = df[selected_chart_col].dropna().value_counts().head(15)
                st.bar_chart(chart_df)
            else:
                st.line_chart(df[selected_chart_col].dropna().reset_index(drop=True))
        else:
            st.info("No numeric columns available for charting.")

        # -------- COLUMN TYPES --------
        st.subheader("📋 Column Types")
        dtype_df = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values
        })
        st.table(dtype_df)

        # -------- BUSINESS FLAGS --------
        st.subheader("🚨 Business Flags")
        flags_found = False

        if "amount_inr" in [c.lower() for c in df.columns]:
            real_col = [c for c in df.columns if c.lower() == "amount_inr"][0]
            if df[real_col].isna().sum() > 0:
                st.warning("Amount_INR has missing values. Financial totals may be incomplete.")
                flags_found = True

        if "revenue_inr" in [c.lower() for c in df.columns]:
            real_col = [c for c in df.columns if c.lower() == "revenue_inr"][0]
            if df[real_col].isna().sum() > 0:
                st.warning("Revenue_INR has missing values. Revenue reporting may be incomplete.")
                flags_found = True

        if invalid_date_summary:
            st.warning("Invalid dates detected. Time-based trends and monthly reports may be unreliable.")
            flags_found = True

        if int(df.duplicated().sum()) > 0:
            st.warning("Duplicate records detected. Spend/revenue could be overstated.")
            flags_found = True

        if not flags_found:
            st.success("No major business reporting flags detected at a basic level.")

        # -------- RECOMMENDATIONS --------
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

        if invalid_date_summary:
            st.warning("Fix invalid date formats before building time-based charts or reports.")
            issues_found = True

        if standardized_text_cols:
            st.info("Use standardized labels for departments, categories, vendors, and regions.")
        st.info("Validate business logic before doing final reporting or dashboarding.")

        if not issues_found:
            st.success("Your dataset looks clean at a basic level. You can move to deeper business analysis.")

        # -------- DOWNLOAD REPORT --------
        st.subheader("📄 Download Summary Report")
        report_text = build_summary_text(
            file_name=uploaded_file.name,
            rows=df.shape[0],
            cols=df.shape[1],
            duplicates=int(df.duplicated().sum()),
            missing_df=missing_df,
            negative_df=negative_df,
            numeric_summary=numeric_summary,
            invalid_date_summary=invalid_date_summary,
            standardized_text_cols=standardized_text_cols
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
