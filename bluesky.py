import os
from atproto import Client
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration 
topic = "Elon Musk"
limit = 100

BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "hw5_bluesky"
COLLECTION_NAME = "posts"

if not all([BLUESKY_HANDLE, BLUESKY_PASSWORD, MONGO_URI]):
    raise EnvironmentError(
        "Missing credentials. Create a .env file with BLUESKY_HANDLE, "
        "BLUESKY_PASSWORD, and MONGO_URI. See .env.example for the template."
    )

# Step 1: Fetch from Bluesky API
client = Client()
client.login(BLUESKY_HANDLE, BLUESKY_PASSWORD)

print(f"\nSearching for posts about: {topic}")

params_data = {"q": topic, "limit": limit}
response = client.app.bsky.feed.search_posts(params=params_data)

data = []
for item in response.posts:
    post = getattr(item, "post", item)

    author_obj = getattr(post, "author", None)
    record_obj = getattr(post, "record", None)

    author_handle = getattr(author_obj, "handle", "") if author_obj else ""
    text = getattr(record_obj, "text", "") if record_obj else ""

    data.append({
        "topic": topic,
        "author": author_handle,
        "text": text[:80],
        "replyCount": getattr(post, "reply_count", 0) or 0,
        "repostCount": getattr(post, "repost_count", 0) or 0,
        "likeCount": getattr(post, "like_count", 0) or 0,
        "quoteCount": getattr(post, "quote_count", 0) or 0,
    })

df = pd.DataFrame(data)
df["totalEngagement"] = (
    df["replyCount"] + df["repostCount"] + df["likeCount"] + df["quoteCount"]
)

print("\n=== BLUESKY DATAFRAME ===")
print(f"Rows pulled from Bluesky: {len(df)}")
print(df.head(10))

# Step 2: Store in MongoDB 
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

docs = df.to_dict("records")
for d in docs:
    d["storedAt"] = datetime.utcnow()

collection.delete_many({"topic": topic})
insert_result = collection.insert_many(docs)
print(f"\nInserted into MongoDB: {len(insert_result.inserted_ids)} documents")

# Step 3: Re-fetch from MongoDB
mongo_docs = list(collection.find({"topic": topic}, {"_id": 0}))
df_mongo = pd.DataFrame(mongo_docs)

print("\n=== MONGODB DATAFRAME ===")
print(f"Rows pulled from MongoDB: {len(df_mongo)}")
print(df_mongo.head(10))

# Step 4: Visualizations
sns.set_theme(style="whitegrid")

# Chart 1: Engagement Share (%)
totals = df_mongo[["replyCount", "repostCount", "likeCount", "quoteCount"]].sum()
share_df = (totals / totals.sum()).reset_index()
share_df.columns = ["EngagementType", "Share"]
share_df["SharePercent"] = share_df["Share"] * 100

plt.figure(figsize=(8, 6))
sns.barplot(data=share_df, x="EngagementType", y="SharePercent")
plt.title(f"Chart 1: Engagement Share (%) — '{topic}'")
plt.ylabel("Percent of Total Engagement")
plt.xlabel("Engagement Type")
plt.tight_layout()
plt.show()

# Chart 2: Distribution of Total Engagement
plt.figure(figsize=(8, 6))
sns.histplot(df_mongo["totalEngagement"], bins=20, kde=True)
plt.title(f"Chart 2: Engagement Distribution — '{topic}'")
plt.xlabel("Total Engagement")
plt.ylabel("Number of Posts")
plt.tight_layout()
plt.show()

# Chart 3: Likes vs Replies
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df_mongo, x="replyCount", y="likeCount")
plt.title(f"Chart 3: Likes vs Replies — '{topic}'")
plt.xlabel("Reply Count")
plt.ylabel("Like Count")
plt.tight_layout()
plt.show()

# Chart 4: Top 10 Posts by Total Engagement
top10 = df_mongo.sort_values("totalEngagement", ascending=False).head(10).copy()
top10["short_text"] = top10["text"].fillna("").apply(
    lambda t: (t[:35] + "...") if len(t) > 35 else t
)

plt.figure(figsize=(10, 6))
sns.barplot(data=top10, y="short_text", x="totalEngagement", orient="h")
plt.title(f"Chart 4: Top 10 Posts by Engagement — '{topic}'")
plt.xlabel("Total Engagement")
plt.ylabel("Post Preview")
plt.tight_layout()
plt.show()
