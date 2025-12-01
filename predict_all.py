import pandas as pd
import joblib

# Load the trained model and dataset
model = joblib.load("protocol_predictor.pkl")
df = pd.read_csv("dataset_ready.csv")

# Predict only using the feature(s) used in training
df["model_prediction"] = model.predict(df[["latency"]])
df["model_protocol"] = df["model_prediction"].map({0: "HTTP/2", 1: "HTTP/3"})

# Display predictions
print("\n--- Model Predictions on Historical Data ---")
print(df[["latency", "http2_time", "http3_time", "better_protocol", "model_protocol"]])

# Calculate how often the model matched real data
correct = (df["better_protocol"] == df["model_protocol"]).mean() * 100
print(f"\nModel Match with Ground Truth: {correct:.2f}%")

# Analyze which protocol performed better overall
http2_avg = df[df["better_protocol"] == "HTTP/2"]["http2_time"].mean()
http3_avg = df[df["better_protocol"] == "HTTP/3"]["http3_time"].mean()
http2_count = (df["better_protocol"] == "HTTP/2").sum()
http3_count = (df["better_protocol"] == "HTTP/3").sum()

print("\n--- Protocol Performance Summary ---")
print(f"HTTP/2 chosen {http2_count} times | Average time: {http2_avg:.6f} s")
print(f"HTTP/3 chosen {http3_count} times | Average time: {http3_avg:.6f} s")

# Provide an automatic conclusion
print("\n--- Conclusion ---")
if http3_count > http2_count and http3_avg < http2_avg:
    conclusion_text = ("HTTP/3 consistently outperformed HTTP/2 in most tests, "
                       "delivering lower average response times. This suggests that "
                       "HTTP/3 (based on QUIC) is more efficient under your network conditions.")
elif http2_count > http3_count:
    conclusion_text = ("HTTP/2 was faster in more tests, suggesting that your network is stable "
                       "and benefits from HTTP/2's lower overhead over TCP.")
else:
    conclusion_text = ("Performance between HTTP/2 and HTTP/3 was nearly equal, indicating that "
                       "both protocols handle your current network conditions similarly.")

print(conclusion_text)


# GUI SECTION 


import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Network Protocol Performance Dashboard")
root.geometry("950x650")

# Title
title_label = tk.Label(root, text="Network Protocol Performance Dashboard",
                       font=("Arial", 20, "bold"))
title_label.pack(pady=10)

# Accuracy
accuracy_label = tk.Label(root, text=f"Model Accuracy: {correct:.2f}%",
                          font=("Arial", 14))
accuracy_label.pack(pady=5)

# Protocol Summary Frame
summary_frame = tk.Frame(root)
summary_frame.pack(pady=10)

# HTTP/2 Summary
http2_frame = tk.LabelFrame(summary_frame, text="HTTP/2 Summary", padx=10, pady=10)
http2_frame.grid(row=0, column=0, padx=20)

tk.Label(http2_frame, text=f"Times Chosen: {http2_count}", font=("Arial", 12)).pack(anchor="w")
tk.Label(http2_frame, text=f"Average Time: {http2_avg:.6f} s", font=("Arial", 12)).pack(anchor="w")

# HTTP/3 Summary
http3_frame = tk.LabelFrame(summary_frame, text="HTTP/3 Summary", padx=10, pady=10)
http3_frame.grid(row=0, column=1, padx=20)

tk.Label(http3_frame, text=f"Times Chosen: {http3_count}", font=("Arial", 12)).pack(anchor="w")
tk.Label(http3_frame, text=f"Average Time: {http3_avg:.6f} s", font=("Arial", 12)).pack(anchor="w")

# Conclusion Frame
conclusion_frame = tk.LabelFrame(root, text="Conclusion", padx=10, pady=10)
conclusion_frame.pack(pady=10)

tk.Label(conclusion_frame, text=conclusion_text, font=("Arial", 12), wraplength=900).pack(anchor="w")


# Scrollable Data Table


table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, pady=10)

columns = ["latency", "http2_time", "http3_time", "better_protocol", "model_protocol"]

tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

# Headings
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)

# Insert Data Rows
for _, row in df[columns].iterrows():
    tree.insert("", "end", values=list(row))

# Scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)

scrollbar.pack(side="right", fill="y")
tree.pack(side="left", fill="both", expand=True)

root.mainloop()
