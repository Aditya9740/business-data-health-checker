import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Business Data Health Checker",
    page_icon="📊",
    layout="wide",
)

# ---------- PREMIUM UI ----------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        color: #f8fafc;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    h1, h2, h3 {
        color: #f8fafc !important;
    }
    .hero-card {
        background: linear-gradient(135deg, rgba(59,130,246,0.18), rgba(16,185,129,0.12));
        border: 1px solid rgba(255,255,255,0.08);
        padding: 1.25rem 1.25rem 1rem 1.25rem;
        border-radius: 18px;
        margin-bottom: 1rem;
    }
    .section-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 1rem;
        border-radius: 16px;
        margin-bottom: 1rem;
    }
    .small-note {
        color: #cbd5e1;
        font-size: 0.95rem;
    }
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 14px;
        border-radius: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <h1>📊 Business Data Health Checker</h1>
        <p class="small-note">
            Upload your CSV or Excel file and get a quick audit of data quality,
            reporting risks, and business issues.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info("🔍 This is a quick automated check. For deeper insights, I provide detailed business analysis and dashboards.")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])


# ---------- HELPERS ----------
def load_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    if file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    return None


def clean_numeric_series(series):
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace(r"[^\d\.\-]", "", regex=True)
        .str.strip()
        .replace(["", "nan", "None", "NaN"], pd.NA)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def standardize_text(series):
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .replace("nan", pd.NA)
    )


def build_summary_text(
    file_name,
    rows,
    cols,
    duplicates,
    missing_df,
    negative_df,
    numeric_summary,
    invalid_date_summary,
    standardized_text_cols,
    top_vendor_text,
    top_category_text,
):
    lines = []
    lines.append("Business Data Health Checker - Client Audit Report")
    lines.append("=" * 60)
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

    lines.append("Business Highlights")
    lines.append("-" * 25)
    lines.append(top_vendor_text)
    lines.append(top_category_text)
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
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📌 Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # -------- AUTO CLEAN NUMERIC-LIKE COLUMNS --------
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🛠 Auto Cleaning")

        cleaned_numeric_cols = []
        financial_keywords = ["amount", "revenue", "cost", "price", "spend", "sales", "value"]

        financial_cols = [
            col for col in df.columns
            if any(keyword in col.lower() for keyword in financial_keywords)
        ]

        for col in financial_cols:
            cleaned_col = clean_numeric_series(df[col])
            if cleaned_col.notna().sum() > 0:
                df[col] = cleaned_col
                cleaned_numeric_cols.append(col)

        remaining_object_cols = [
            col for col in df.columns
            if df[col].dtype == "object" and col not in cleaned_numeric_cols
        ]

        for col in remaining_object_cols:
            cleaned_col = clean_numeric_series(df[col])
            original_non_null = df[col].notna().sum()
            cleaned_non_null = cleaned_col.notna().sum()

            if original_non_null > 0 and (cleaned_non_null / original_non_null) >= 0.6:
                df[col] = cleaned_col
                cleaned_numeric_cols.append(col)

        if cleaned_numeric_cols:
            st.success(f"Converted to numeric: {', '.join(cleaned_numeric_cols)}")
        else:
            st.info("No messy numeric-like columns needed conversion.")
        st.markdown("</div>", unsafe_allow_html=True)

        # -------- DATE VALIDATION --------
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📅 Date Validation")

        date_cols = [col for col in df.columns if "date" in col.lower()]
        invalid_date_summary = {}

        if date_cols:
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
                st.dataframe(invalid_date_df, use_container_width=True)
            else:
                st.success("No invalid date issues found.")
        else:
            st.info("No date-like columns detected.")
        st.markdown("</div>", unsafe_allow_html=True)

        # -------- TEXT STANDARDIZATION --------
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)

        # -------- SUMMARY --------
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📊 Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", df.shape[0])
        col2.metric("Total Columns", df.shape[1])
        col3.metric("Duplicate Rows", int(df.duplicated().sum()))
        st.markdown("</div>", unsafe_allow_html=True)

        # -------- DATA ISSUES --------
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
            st.dataframe(missing_df, use_container_width=True)
        else:
            missing_df = pd.DataFrame()
            st.success("No missing values found.")
        st.markdown("</div>", unsafe_allow_html=True)

        # -------- NEGATIVE VALUE DETECTION --------
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
            st.dataframe(negative_df, use_container_width=True)
        else:
            negative_df = pd.DataFrame()
            st.success("No negative numeric values found.")
        st.markdown("</div>", unsafe_allow_html=True)

        # -------- KPI TOTALS --------
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("💰 Top-Level KPI Totals")

        numeric_summary = {}
        if numeric_cols:
            for col in numeric_cols[:6]:
                numeric_summary[col] = float(df[col].sum(skipna=True))

            kpi_cols = st.columns(min(max(len(numeric_summary), 1), 3))
            idx = 0
            for col_name, total_value in numeric_summary.items():
                kpi_cols[idx % len(kpi_cols)].metric(f"Total {col_name}", f"{total_value:,.2f}")
                idx += 1
        else:
            st.info("No numeric columns available for KPI totals.")
        st.markdown("</div>", unsafe_allow_html=True)

        # -------- BUSINESS INSIGHTS --------
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🧠 Quick Business Insights")

        top_vendor_text = "Top vendor insight not available."
        top_category_text = "Top category insight not available."

        if "vendor" in [c.lower() for c in df.columns] and "amount_inr" in [c.lower() for c in df.columns]:
            vendor_col = [c for c in df.columns if c.lower() == "vendor"][0]
            amount_col = [c for c in df.columns if c.lower() == "amount_inr"][0]
            vendor_summary = (
                df.groupby(vendor_col, dropna=True)[amount_col]
                .sum(min_count=1)
                .sort_values(ascending=False)
            )
            if not vendor_summary.empty:
                top_vendor = vendor_summary.index[0]
                top_vendor_value = vendor_summary.iloc[0]
                top_vendor_text = f"Highest spend vendor: {top_vendor} ({top_vendor_value:,.2f})"
                st.info(top_vendor_text)

        if "category" in [c.lower() for c in df.columns] and "amount_inr" in [c.lower() for c in df.columns]:
            category_col = [c for c in df.columns if c.lower() == "category"][0]
            amount_col = [c for c in df.columns if c.lower() == "amount_inr"][0]
            category_summary = (
                df.groupby(category_col, dropna=True)[amount_col]
                .sum(min_count=1)
                .sort_values(ascending=False)
            )
            if not category_summary.empty:
                top_category = category_summary.index[0]
                top_category_value = category_summary.iloc[0]
                top_category_text = f"Highest spend category: {top_category} ({top_category_value:,.2f})"
                st.info(top_category_text)
        st.markdown("</div>", unsafe_allow_html=True)

        # -------- BASIC CHARTS --------
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)

        # -------- COLUMN TYPES --------
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📋 Column Types")
        dtype_df = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values
        })
        st.dataframe(dtype_df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # -------- BUSINESS FLAGS --------
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🚨 Business Flags")
        flags_found = False

        lower_cols = [c.lower() for c in df.columns]

        if "amount_inr" in lower_cols:
            real_col = [c for c in df.columns if c.lower() == "amount_inr"][0]
            if df[real_col].isna().sum() > 0:
                st.warning("Amount_INR has missing values. Financial totals may be incomplete.")
                flags_found = True

        if "revenue_inr" in lower_cols:
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

        if not negative_df.empty:
            st.warning("Negative financial values detected. Review whether these are refunds, credits, or data issues.")
            flags_found = True

        if not flags_found:
            st.success("No major business reporting flags detected at a basic level.")
        st.markdown("</div>", unsafe_allow_html=True)

        # -------- RECOMMENDATIONS --------
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)

        # -------- DOWNLOAD REPORT --------
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
            standardized_text_cols=standardized_text_cols,
            top_vendor_text=top_vendor_text,
            top_category_text=top_category_text,
        )

        st.download_button(
            label="Download Report (.txt)",
            data=report_text,
            file_name="business_data_health_report.txt",
            mime="text/plain",
        )
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("🚀 Want deeper insights?")
st.write("I provide detailed business data audits, dashboards, and cost optimization analysis.")
st.write("📧 Email: mahajanaditya814@gmail.com")
st.write("🔗 LinkedIn: linkedin.com/in/aditya-mahajan-58b432266")
