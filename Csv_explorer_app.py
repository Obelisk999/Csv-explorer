import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="CSV Explorer", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .main { background-color: #0e0e10; }
    h1, h2, h3 { font-family: 'Space Mono', monospace; }

    .big-title {
        font-family: 'Space Mono', monospace;
        font-size: 2.4rem;
        font-weight: 700;
        color: #f0f0f0;
        letter-spacing: -1px;
    }
    .subtitle {
        color: #888;
        font-size: 1rem;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    .stat-card {
        background: #1a1a1f;
        border: 1px solid #2a2a35;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    .stat-label {
        color: #666;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-family: 'Space Mono', monospace;
    }
    .stat-value {
        color: #e2ff59;
        font-size: 2rem;
        font-weight: 700;
        font-family: 'Space Mono', monospace;
    }
    .section-header {
        font-family: 'Space Mono', monospace;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #555;
        border-bottom: 1px solid #1e1e25;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }
    div[data-testid="stFileUploader"] {
        background: #13131a;
        border: 2px dashed #2a2a40;
        border-radius: 12px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="big-title">📊 CSV Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Drop in a CSV. Explore instantly.</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # ── Stats Row ──────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    for col, label, value in [
        (c1, "Rows", f"{len(df):,}"),
        (c2, "Columns", str(df.shape[1])),
        (c3, "Numeric Cols", str(df.select_dtypes("number").shape[1])),
        (c4, "Missing Values", f"{df.isnull().sum().sum():,}"),
    ]:
        col.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">{label}</div>
                <div class="stat-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["🗂 Data", "📈 Charts", "🔬 Stats", "🚨 Missing"])

    # Tab 1 – Raw data with filter
    with tab1:
        st.markdown('<div class="section-header">Filter & Browse</div>', unsafe_allow_html=True)
        search = st.text_input("Search any value", placeholder="Type to filter rows…")
        display_df = df[df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)] if search else df
        st.dataframe(display_df, use_container_width=True, height=400)
        st.caption(f"Showing {len(display_df):,} of {len(df):,} rows")

    # Tab 2 – Charts
    with tab2:
        st.markdown('<div class="section-header">Visualise</div>', unsafe_allow_html=True)
        num_cols = df.select_dtypes("number").columns.tolist()
        cat_cols = df.select_dtypes(["object", "category"]).columns.tolist()

        chart_type = st.selectbox("Chart type", ["Histogram", "Scatter", "Bar (counts)", "Box Plot", "Correlation Heatmap"])

        if chart_type == "Histogram" and num_cols:
            col = st.selectbox("Column", num_cols)
            fig = px.histogram(df, x=col, template="plotly_dark", color_discrete_sequence=["#e2ff59"])
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Scatter" and len(num_cols) >= 2:
            x_col = st.selectbox("X axis", num_cols, index=0)
            y_col = st.selectbox("Y axis", num_cols, index=1 if len(num_cols) > 1 else 0)
            color_col = st.selectbox("Color by (optional)", ["None"] + cat_cols)
            fig = px.scatter(df, x=x_col, y=y_col,
                             color=None if color_col == "None" else color_col,
                             template="plotly_dark", opacity=0.7)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Bar (counts)" and cat_cols:
            col = st.selectbox("Column", cat_cols)
            top_n = st.slider("Top N categories", 5, 30, 10)
            counts = df[col].value_counts().head(top_n).reset_index()
            counts.columns = [col, "count"]
            fig = px.bar(counts, x=col, y="count", template="plotly_dark",
                         color_discrete_sequence=["#e2ff59"])
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Box Plot" and num_cols:
            col = st.selectbox("Numeric column", num_cols)
            group = st.selectbox("Group by (optional)", ["None"] + cat_cols)
            fig = px.box(df, y=col, x=None if group == "None" else group,
                         template="plotly_dark", color_discrete_sequence=["#e2ff59"])
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Correlation Heatmap" and len(num_cols) >= 2:
            corr = df[num_cols].corr()
            fig = go.Figure(go.Heatmap(
                z=corr.values, x=corr.columns, y=corr.columns,
                colorscale="RdYlGn", zmid=0
            ))
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough columns of the right type for this chart.")

    # Tab 3 – Summary stats
    with tab3:
        st.markdown('<div class="section-header">Descriptive Statistics</div>', unsafe_allow_html=True)
        if num_cols:
            st.dataframe(df[num_cols].describe().T.style.format("{:.2f}"), use_container_width=True)
        else:
            st.info("No numeric columns found.")

    # Tab 4 – Missing values
    with tab4:
        st.markdown('<div class="section-header">Missing Value Analysis</div>', unsafe_allow_html=True)
        missing = df.isnull().sum().reset_index()
        missing.columns = ["Column", "Missing"]
        missing["% Missing"] = (missing["Missing"] / len(df) * 100).round(2)
        missing = missing[missing["Missing"] > 0].sort_values("% Missing", ascending=False)

        if missing.empty:
            st.success("🎉 No missing values found!")
        else:
            fig = px.bar(missing, x="Column", y="% Missing", template="plotly_dark",
                         color="% Missing", color_continuous_scale="OrRd",
                         title="% Missing per Column")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(missing, use_container_width=True)

else:
    st.markdown("""
        <div style="text-align:center; padding: 60px 0; color: #444;">
            <div style="font-size: 3rem;">☝️</div>
            <div style="font-family: 'Space Mono', monospace; font-size: 1rem; margin-top: 12px;">Upload a CSV to get started</div>
        </div>
    """, unsafe_allow_html=True)
