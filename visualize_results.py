import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load processed dataset
df = pd.read_csv("dataset_ready.csv")

# ----------- Scatter Comparison -----------
plt.figure(figsize=(9, 6))
sns.scatterplot(x="latency", y="http2_time", data=df, label="HTTP/2", color="#1f77b4", s=60)
sns.scatterplot(x="latency", y="http3_time", data=df, label="HTTP/3", color="#ff7f0e", s=60)
plt.title("HTTP/2 vs HTTP/3 Performance by Latency", fontsize=14, weight="bold")
plt.xlabel("Network Latency (ms)")
plt.ylabel("Response Time (s)")
plt.legend(title="Protocol", loc="upper left")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

# ----------- Protocol Winner Distribution -----------
plt.figure(figsize=(6, 4))
sns.countplot(x="better_protocol", data=df, palette="Set2")
plt.title("Protocol Performance Distribution", fontsize=13, weight="bold")
plt.xlabel("Faster Protocol")
plt.ylabel("Number of Cases")
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
