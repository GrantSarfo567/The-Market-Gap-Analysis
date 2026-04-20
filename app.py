# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# CONFIG

st.set_page_config(layout="wide")


# LOAD DATA

@st.cache_data
def load_data():
    return pd.read_csv(".clean_snacks.csv")

df = load_data()

# SIDEBAR → MARKET LENS

st.sidebar.title("Market Lens")

st.sidebar.markdown("""
Refine how the market is viewed.

This is not just filtering, it defines how opportunity is evaluated.
""")

category_focus = st.sidebar.selectbox(
    "Market Focus",
    [
        "All Snacks",
        "Indulgent (Sweet Snacks)",
        "Better-for-You (Nuts & Seeds)",
        "Functional (Protein-Oriented)"
    ]
)

if category_focus == "Indulgent (Sweet Snacks)":
    df = df[df['primary_category'].isin(["Chocolate & Candy", "Biscuits & Cookies"])]

elif category_focus == "Better-for-You (Nuts & Seeds)":
    df = df[df['primary_category'].isin(["Nuts & Seeds"])]

elif category_focus == "Functional (Protein-Oriented)":
    df = df[df['proteins_100g'] > 8]

# Nutritional thresholds
st.sidebar.markdown("### Opportunity Definition")

sugar_limit = st.sidebar.slider("Max Sugar (g)", 0, 50, 10)
protein_min = st.sidebar.slider("Min Protein (g)", 0, 30, 8)


# DEFINE OPPORTUNITY

df['is_opportunity'] = (
    (df['sugars_100g'] <= sugar_limit) &
    (df['proteins_100g'] >= protein_min)
)


# HERO (CENTERED)

st.markdown("""
<div style='text-align: center;'>
    <h1>Healthy Snack Market Opportunity</h1>
    <h3>Where can we build a product that delivers strong health value with limited competition?</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# EXECUTIVE INSIGHT

st.markdown("""
### Executive Insight

The snack market is heavily concentrated in sugar-driven products, while healthier options remain underdeveloped.

Segments combining lower sugar with higher protein contain significantly fewer products, indicating a clear gap between supply and evolving consumer demand.
""")


# KPI

col1, col2, col3, col4 = st.columns(4)

col1.metric("Products", len(df))
col2.metric("Avg Sugar", f"{df['sugars_100g'].mean():.1f}g")
col3.metric("Avg Protein", f"{df['proteins_100g'].mean():.1f}g")
col4.metric("Opportunity Share", f"{df['is_opportunity'].mean()*100:.1f}%")

st.divider()


# SCATTER

st.subheader("Market Structure")

fig = px.scatter(
    df,
    x="sugars_100g",
    y="proteins_100g",
    color=df['is_opportunity'].map({True: "Opportunity Zone", False: "Crowded Market"}),
    color_discrete_map={
        "Opportunity Zone": "#2ecc71",
        "Crowded Market": "#bdc3c7"
    },
    hover_data=["primary_category"],
    height=550
)

fig.add_vline(x=sugar_limit, line_dash="dash", line_color="red")
fig.add_hline(y=protein_min, line_dash="dash", line_color="green")

st.plotly_chart(fig, use_container_width=True)

st.caption("Green points highlight products that meet opportunity criteria.")


# HEATMAP

st.subheader("Market Density")

heatmap = df.groupby(
    ['sugar_bin', 'protein_bin'],
    observed=False
).size().unstack(fill_value=0)

fig2 = px.imshow(
    heatmap,
    text_auto=True,
    color_continuous_scale="Blues",
    aspect="auto",
    height=500
)


# CANDIDATE'S CHOICE (HEALTH SCORE)

st.subheader("Candidate’s Choice: Health Score vs Market Density")

st.markdown("""
To better capture real-world product value, a **Health Score** was introduced.

This combines:
- Lower sugar (better)
- Higher protein (better)
- Lower competition (better)

This allows us to identify not just gaps, but **high-value gaps**.
""")

segment_scores = df.groupby(
    ['sugar_bin', 'protein_bin'],
    observed=False
).agg(
    count=('product_name', 'count'),
    avg_protein=('proteins_100g', 'mean'),
    avg_sugar=('sugars_100g', 'mean')
).reset_index()

segment_scores['score'] = (
    segment_scores['avg_protein'] -
    segment_scores['avg_sugar'] -
    np.log1p(segment_scores['count'])
)

top_segments = segment_scores.sort_values('score', ascending=False)

best_segment = top_segments.iloc[0]

# Highlight best segment
fig2.add_annotation(
    x=best_segment['protein_bin'],
    y=best_segment['sugar_bin'],
    text="Best Opportunity",
    showarrow=True,
    arrowhead=2,
    font=dict(color="red", size=12)
)

st.plotly_chart(fig2, use_container_width=True)

# MARKET DENSITY EXPLANATION

st.info("""
**Market Density** shows how crowded each segment is:

- Dark = many products (high competition)
- Light = fewer products (opportunity)

This helps identify where new products can stand out.
""")


# OPPORTUNITY RANKING TABLE

st.subheader("Top Opportunity Segments")

st.dataframe(top_segments.head(5), use_container_width=True)


# BEST SEGMENT CALLOUT

st.success(f"""
**Top Opportunity Identified**

- Sugar: {best_segment['sugar_bin']}
- Protein: {best_segment['protein_bin']}

This segment combines strong nutritional value with low competition.
""")


# FINAL RECOMMENDATION

st.subheader("Strategic Recommendation")

st.markdown("""
The strongest opportunity lies in developing products that combine:

- High protein  
- Low sugar  
- Clean, functional ingredients  

Recommended formats:
- Protein snack bars  
- Nut and seed clusters  
- Functional healthy snacks  

These products align with health trends while avoiding saturated segments.
""")

st.markdown("---")

st.caption("Built as a data-driven exploration of market gaps in the healthy snack space.")