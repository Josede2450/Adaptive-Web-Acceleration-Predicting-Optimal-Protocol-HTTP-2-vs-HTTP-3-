import pandas as pd


# Load raw collected data

data = pd.read_csv("network_data.csv")

# Drop any invalid or incomplete rows
data = data.dropna(subset=["latency", "protocol", "time"])


# Group and analyze by latency

result = []

for latency, group in data.groupby("latency"):
    # Compute mean times for HTTP/2 and HTTP/3
    t2 = group[group["protocol"] == "HTTP/2"]["time"].mean()
    t3 = group[group["protocol"] == "HTTP/3"]["time"].mean()

    # Only include valid comparisons
    if pd.notnull(t2) and pd.notnull(t3):
        better = "HTTP/3" if t3 < t2 else "HTTP/2"
        result.append([latency, t2, t3, better])


# Create cleaned dataset

df = pd.DataFrame(result, columns=["latency", "http2_time", "http3_time", "better_protocol"])

# Save processed dataset
df.to_csv("dataset_ready.csv", index=False)

print("Dataset successfully processed and saved to 'dataset_ready.csv'")
print(df.head())
