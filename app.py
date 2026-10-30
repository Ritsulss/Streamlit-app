"""
Biscayne Bay Water Quality Explorer
-----------------------------------
An interactive Streamlit app for exploring water-quality data collected by an
autonomous underwater vehicle (AUV) in Biscayne Bay, Florida.

Run locally:  streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Biscayne Bay Water Quality",
    page_icon="🌊",
    layout="wide",
)

DATA_PATH = Path(__file__).parent / "data" / "biscayneBay_waterquality.csv"

# Friendly names for the water-quality parameters we expose to the user.
# key = column in the CSV, value = (label shown in the app, unit, short description)
PARAMETERS = {
    "Temp C": ("Water Temperature", "°C", "Temperature of the water measured by the sonde."),
    "Sal ppt": ("Salinity", "ppt", "Dissolved salt content. Open ocean water is about 35 ppt."),
    "pH": ("pH", "", "Acidity/alkalinity. Healthy seawater is typically 7.8–8.3."),
    "ODO mg/L": ("Dissolved Oxygen", "mg/L", "Oxygen available to marine life. Below ~4 mg/L stresses fish; below 2 mg/L is hypoxic."),
    "ODOsat %": ("Dissolved Oxygen Saturation", "%", "Oxygen as a percentage of what the water could hold at saturation."),
    "Turbid+ NTU": ("Turbidity", "NTU", "Cloudiness of the water caused by suspended particles."),
    "Chl ug/L": ("Chlorophyll", "µg/L", "Proxy for algae (phytoplankton) abundance."),
    "SpCond mS/cm": ("Specific Conductance", "mS/cm", "Ability of water to conduct electricity, closely tied to salinity."),
    "Total Water Column (m)": ("Total Water Depth", "m", "Distance from the surface to the sea floor at the vehicle's location."),
}


def label(col: str) -> str:
    """Return a readable axis label like 'Salinity (ppt)'."""
    name, unit, _ = PARAMETERS[col]
    return f"{name} ({unit})" if unit else name


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()  # some headers have trailing spaces

    # Build a real timestamp from the sonde's date + time columns
    df["Timestamp"] = pd.to_datetime(
        df["Date m/d/y"].astype(str).str.strip() + " " + df["Time hh:mm:ss"].astype(str).str.strip(),
        format="%m/%d/%y %H:%M:%S",
        errors="coerce",
    )
    df = df.dropna(subset=["Timestamp", "Latitude", "Longitude"])
    df["Minutes Elapsed"] = (df["Timestamp"] - df["Timestamp"].min()).dt.total_seconds() / 60
    return df


try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"Could not find the dataset at `{DATA_PATH}`. Make sure the CSV is in the `data/` folder.")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar — user inputs
# ---------------------------------------------------------------------------
st.sidebar.header("🔧 Controls")

param = st.sidebar.selectbox(
    "Water-quality parameter",
    options=list(PARAMETERS.keys()),
    format_func=lambda c: PARAMETERS[c][0],
    help="Choose which measurement to color the map and plot over time.",
)

max_min = float(df["Minutes Elapsed"].max())
time_range = st.sidebar.slider(
    "Survey time window (minutes from start)",
    min_value=0.0,
    max_value=round(max_min, 1),
    value=(0.0, round(max_min, 1)),
    step=0.5,
)

compare_param = st.sidebar.selectbox(
    "Compare against (scatter plot)",
    options=[c for c in PARAMETERS if c != param],
    format_func=lambda c: PARAMETERS[c][0],
)

show_trend = st.sidebar.checkbox("Show rolling average on time-series", value=True)
show_raw = st.sidebar.checkbox("Show raw data table", value=False)

# Apply the time filter
filtered = df[df["Minutes Elapsed"].between(*time_range)]

# ---------------------------------------------------------------------------
# 1. Overview
# ---------------------------------------------------------------------------
st.title("🌊 Biscayne Bay Water Quality Explorer")
st.markdown(
    """
This app explores water-quality measurements collected by an **autonomous underwater
vehicle (AUV)** during a survey of **Biscayne Bay, Florida**. As the vehicle moved along its
mission track it logged its GPS position along with readings from a water-quality sonde
(temperature, salinity, pH, dissolved oxygen, turbidity, and chlorophyll) about once per second.

Use the **controls in the sidebar** to pick a parameter, narrow the time window, and compare
measurements against each other.
"""
)

st.header("📋 Overview")
start, end = df["Timestamp"].min(), df["Timestamp"].max()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Survey date", start.strftime("%b %d, %Y"))
c2.metric("Duration", f"{(end - start).total_seconds() / 60:.1f} min")
c3.metric("Total readings", f"{len(df):,}")
c4.metric("Readings in window", f"{len(filtered):,}")

if filtered.empty:
    st.warning("No readings fall inside the selected time window. Widen the slider in the sidebar.")
    st.stop()

name, unit, desc = PARAMETERS[param]
st.info(f"**{name}** — {desc}")

s = filtered[param]
m1, m2, m3, m4 = st.columns(4)
m1.metric("Mean", f"{s.mean():.2f} {unit}")
m2.metric("Minimum", f"{s.min():.2f} {unit}")
m3.metric("Maximum", f"{s.max():.2f} {unit}")
m4.metric("Std. deviation", f"{s.std():.2f} {unit}")

# ---------------------------------------------------------------------------
# 2. Data Display — charts
# ---------------------------------------------------------------------------
st.header("📊 Data Display")

tab_map, tab_time, tab_scatter, tab_dist = st.tabs(
    ["🗺️ Map", "📈 Time Series", "🔬 Compare Parameters", "📊 Distribution"]
)

with tab_map:
    st.markdown(
        f"Each point is one reading along the AUV's path, colored by **{name}**. "
        "Hover over a point to see its exact value and time."
    )
    fig_map = px.scatter_map(
        filtered,
        lat="Latitude",
        lon="Longitude",
        color=param,
        color_continuous_scale="Viridis",
        hover_data={"Timestamp": "|%H:%M:%S", param: ":.2f", "Latitude": ":.5f", "Longitude": ":.5f"},
        labels={param: label(param)},
        zoom=17,
        height=550,
        title=f"AUV Survey Track Colored by {name}",
    )
    fig_map.update_layout(map_style="open-street-map", margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(fig_map)

with tab_time:
    st.markdown(f"How **{name}** changed over the course of the survey.")
    ts = filtered[["Timestamp", param]].copy()
    ts = ts.melt(id_vars="Timestamp", var_name="Series", value_name="Value")
    ts["Series"] = "Measured"
    if show_trend:
        roll = filtered[["Timestamp"]].copy()
        roll["Value"] = filtered[param].rolling(30, center=True, min_periods=1).mean()
        roll["Series"] = "30-reading rolling average"
        ts = pd.concat([ts, roll], ignore_index=True)

    fig_ts = px.line(
        ts,
        x="Timestamp",
        y="Value",
        color="Series",
        title=f"{name} Over Time",
        labels={"Timestamp": "Time of Day", "Value": label(param), "Series": "Legend"},
        color_discrete_map={"Measured": "#9ecae1", "30-reading rolling average": "#08519c"},
    )
    st.plotly_chart(fig_ts)

with tab_scatter:
    cname = PARAMETERS[compare_param][0]
    st.markdown(
        f"Is **{name}** related to **{cname}**? Points are colored by water depth so you can "
        "see whether patterns change between shallow and deep areas."
    )
    fig_sc = px.scatter(
        filtered,
        x=compare_param,
        y=param,
        color="Total Water Column (m)",
        color_continuous_scale="Blues",
        title=f"{name} vs. {cname}",
        labels={
            compare_param: label(compare_param),
            param: label(param),
            "Total Water Column (m)": "Water Depth (m)",
        },
        opacity=0.7,
    )
    st.plotly_chart(fig_sc)
    r = filtered[[param, compare_param]].corr().iloc[0, 1]
    strength = "strong" if abs(r) >= 0.7 else "moderate" if abs(r) >= 0.4 else "weak"
    direction = "positive" if r > 0 else "negative"
    st.caption(f"Pearson correlation: **r = {r:.2f}** ({strength} {direction} relationship).")

with tab_dist:
    st.markdown(f"How often each range of **{name}** values was observed.")
    fig_h = px.histogram(
        filtered,
        x=param,
        nbins=40,
        title=f"Distribution of {name}",
        labels={param: label(param), "count": "Number of Readings"},
    )
    fig_h.update_layout(yaxis_title="Number of Readings", bargap=0.05)
    st.plotly_chart(fig_h)

if show_raw:
    st.subheader("Raw data")
    cols = ["Timestamp", "Latitude", "Longitude"] + list(PARAMETERS.keys())
    st.dataframe(filtered[cols])
    st.download_button(
        "⬇️ Download filtered data as CSV",
        filtered[cols].to_csv(index=False).encode("utf-8"),
        file_name="biscayne_bay_filtered.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------------------------
# 3. Insights
# ---------------------------------------------------------------------------
st.header("💡 Insights")

do_mean = filtered["ODO mg/L"].mean()
sal_min, sal_max = filtered["Sal ppt"].min(), filtered["Sal ppt"].max()
sal_depth_r = filtered[["Sal ppt", "Total Water Column (m)"]].corr().iloc[0, 1]

st.markdown(
    f"""
- **Dissolved oxygen** averaged **{do_mean:.2f} mg/L** in this window — above the ~4 mg/L level
  where fish become stressed, so conditions were adequate for marine life during the survey.
- **Salinity** ranged from **{sal_min:.1f} to {sal_max:.1f} ppt**, slightly saltier than typical
  open-ocean water (~35 ppt). Shallow, sun-warmed lagoons like Biscayne Bay can concentrate salt
  through evaporation, especially in the dry season (this survey was in early February).
- Salinity vs. water depth correlation is **r = {sal_depth_r:.2f}**. Try the *Compare Parameters*
  tab with *Salinity* and *Total Water Depth* to explore this yourself.
- **pH** stayed very stable (about 7.73–7.77), slightly below the typical seawater range.
- **Temperature** barely changed (about 0.5 °C range), which is expected for a short survey
  in a small area.
"""
)

st.warning(
    "**Data-quality note:** Every turbidity reading and most chlorophyll readings (~78%) are "
    "**negative**, which is "
    "not physically possible. This usually means the optical sensors needed recalibration (an offset "
    "error). Treat those two parameters as *relative* changes rather than absolute values."
)

st.markdown("---")
st.caption(
    "Data: AUV water-quality survey, Biscayne Bay, FL (Feb 4, 2022). "
    "Built with Streamlit and Plotly."
)
