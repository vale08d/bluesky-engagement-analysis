# 🦋 Bluesky Engagement Analysis

> A full-stack data pipeline that pulls live posts from the Bluesky social API, stores them in MongoDB Atlas, and generates engagement visualizations with Python.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Bluesky](https://img.shields.io/badge/API-Bluesky%20AT%20Protocol-0085FF?style=flat)
![MongoDB](https://img.shields.io/badge/Database-MongoDB%20Atlas-47A248?style=flat&logo=mongodb&logoColor=white)
![Pandas](https://img.shields.io/badge/Data-Pandas-150458?style=flat&logo=pandas&logoColor=white)
![Seaborn](https://img.shields.io/badge/Visualization-Seaborn-4C72B0?style=flat)

---

## 📌 What This Project Does

This pipeline performs end-to-end social media data engineering on any search topic:

1. **Fetches** up to 100 live posts from Bluesky's AT Protocol API via `atproto`
2. **Structures** raw API responses into a clean Pandas DataFrame (author, text, reply/repost/like/quote counts)
3. **Calculates** a composite `totalEngagement` score per post
4. **Persists** results to MongoDB Atlas with timestamps — replacing stale data on each run
5. **Re-reads** from MongoDB to confirm data integrity before visualization
6. **Generates 4 charts** analyzing engagement patterns across the fetched dataset

---

## 📊 Visualizations Generated

| Chart | Type | What It Shows |
|-------|------|---------------|
| Engagement Share (%) | Bar | Which interaction type (likes, reposts, replies, quotes) dominates |
| Engagement Distribution | Histogram + KDE | How engagement is spread across posts — skew, outliers |
| Likes vs Replies | Scatter | Correlation between reply and like behavior |
| Top 10 Posts | Horizontal Bar | Highest-engagement posts with text previews |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3 | Core scripting |
| atproto | Bluesky AT Protocol API client |
| Pandas | Data structuring and transformation |
| MongoDB Atlas | Cloud database — storage and retrieval |
| pymongo | Python MongoDB driver |
| Seaborn + Matplotlib | Statistical visualizations |

---

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/vale08d/bluesky-engagement-analysis.git
cd bluesky-engagement-analysis
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure credentials (environment variables — do NOT hardcode)

Create a `.env` file in the project root:
```
BLUESKY_HANDLE=your_handle@bsky.social
BLUESKY_PASSWORD=your_app_password
MONGO_URI=your_mongodb_atlas_connection_string
```

> ⚠️ **Never commit credentials to GitHub.** The `.gitignore` file in this repo excludes `.env`.
> Generate a Bluesky **App Password** at: Settings → Privacy & Security → App Passwords

### 4. Run the pipeline
```bash
python bluesky.py
```

---

## 🔄 How It Works

```
Bluesky API (atproto)
       │
       ▼
  Raw post objects
       │
       ▼
  Pandas DataFrame ──► totalEngagement column added
       │
       ▼
  MongoDB Atlas (insert with timestamp)
       │
       ▼
  Re-fetch from MongoDB ──► Verify data integrity
       │
       ▼
  4 Seaborn charts generated
```

---

## 📁 Project Structure

```
bluesky-engagement-analysis/
├── bluesky.py           # Main pipeline script
├── requirements.txt     # Python dependencies
├── .gitignore           # Excludes .env and credentials
├── .env.example         # Template for environment variables
└── README.md
```

---

## 💡 What I Learned

- **API response parsing:** Bluesky's AT Protocol returns deeply nested objects with optional fields — using `getattr()` with fallbacks was essential to avoid crashes on posts with missing metadata.
- **MongoDB upsert pattern:** Deleting and re-inserting by topic on each run keeps the collection current without accumulating stale records.
- **Engagement skew:** Social media engagement almost always follows a power-law distribution — a small number of posts capture the majority of interactions. The histogram + KDE chart makes this pattern immediately visible.

---

## 📸 Sample Output

*(Add screenshots of your 4 charts here)*
