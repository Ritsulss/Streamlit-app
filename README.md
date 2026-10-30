# 🌊 Biscayne Bay Water Quality Explorer

An interactive **Streamlit** web app for exploring water-quality data collected by an
autonomous underwater vehicle (AUV) in Biscayne Bay, Florida.

🔗 **Live app:** https://YOUR-APP-NAME.streamlit.app  *(replace after deploying)*
🔗 **Repository:** https://github.com/YOUR-USERNAME/biscayne-bay-app  *(replace)*

---

## Purpose

Biscayne Bay is a shallow subtropical lagoon next to Miami whose health is affected by
nutrient runoff, freshwater inflow, and heat. This app lets anyone, without writing code,
explore how water conditions vary across space and time during an AUV survey:

- See **where** readings were taken on an interactive map, colored by any parameter
- See **how** a parameter changed over the survey with a time-series chart
- Check whether two parameters are **related** (e.g., salinity vs. depth)
- Read plain-language **insights** about what the numbers mean

## Dataset

**File:** `data/biscayneBay_waterquality.csv`

| Property | Value |
|---|---|
| Location | Biscayne Bay, FL (≈ 25.912° N, 80.137° W) |
| Date | February 4, 2022, 16:18 – 16:34 |
| Rows | 942 readings (~1 per second) |
| Columns | 69 (vehicle navigation, battery, DVL, and sonde measurements) |

The app focuses on these sonde measurements:

| Parameter | Unit |
|---|---|
| Water temperature | °C |
| Salinity | ppt |
| pH | – |
| Dissolved oxygen (concentration & saturation) | mg/L, % |
| Turbidity | NTU |
| Chlorophyll | µg/L |
| Specific conductance | mS/cm |
| Total water depth | m |

> ⚠️ **Data-quality note:** All turbidity readings and most chlorophyll readings are negative,
> which points to a sensor calibration offset. The app flags this and suggests treating those
> parameters as relative rather than absolute.

## How to use the app

1. **Pick a parameter** in the sidebar (e.g., *Dissolved Oxygen*). The summary statistics, map,
   time series, and histogram all update.
2. **Drag the time-window slider** to focus on part of the survey.
3. **Choose a comparison parameter** to see a scatter plot and correlation coefficient in the
   *Compare Parameters* tab.
4. Toggle **"Show rolling average"** to smooth the time-series line.
5. Toggle **"Show raw data table"** to view and download the filtered data as CSV.

### App sections
- **Overview** – what the data is, key metrics, and summary statistics
- **Data Display** – four Plotly charts in tabs: map, time series, parameter comparison, distribution
- **Insights** – plain-language findings that update with your selected time window

## Run locally

```bash
git clone https://github.com/YOUR-USERNAME/biscayne-bay-app.git
cd biscayne-bay-app
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501.

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub (public).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app → Deploy a public app from GitHub**.
4. Select the repo, branch `main`, and main file `app.py`. Click **Deploy**.
5. Copy the app URL into the top of this README.

## Project structure

```
biscayne-bay-app/
├── app.py                 # Streamlit application
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── AGILE.md               # Agile process: backlog, sprints, retrospectives
├── .streamlit/config.toml # Theme
└── data/
    └── biscayneBay_waterquality.csv
```

## Agile process

This project was managed with Agile (Scrum-style) practices: user stories, a prioritized
product backlog, short sprints, a Kanban board (GitHub Projects), and retrospectives.
See **[AGILE.md](AGILE.md)** for details.

## Tech stack

Python · Streamlit · Pandas · Plotly
