import subprocess
import joblib
import re
import platform
import pandas as pd
import numpy as np

# Load trained model
model = joblib.load("protocol_predictor.pkl")

# Detect OS type
IS_WINDOWS = platform.system().lower().startswith("win")

def get_latency(host="8.8.8.8"):
    """Ping a host and extract the average latency (ms)."""
    try:
        cmd = ["ping", "-n", "3", host] if IS_WINDOWS else ["ping", "-c", "3", host]
        output = subprocess.check_output(cmd, universal_newlines=True)
        
        if IS_WINDOWS:
            match = re.search(r"Average = (\d+)ms", output)
            if match:
                return float(match.group(1))
        else:
            match = re.search(r"rtt.* = .*?/([\d\.]+)/", output)
            if match:
                return float(match.group(1))
    except Exception as e:
        print("Ping error:", e)
    return None


def describe_condition(latency):
    """Classify and describe current network condition."""
    if latency <= 15:
        return "Low latency (fast and stable network)", "In low-latency environments, HTTP/2 can perform well since TCP overhead is minimal."
    elif latency <= 30:
        return "Medium latency (moderate delay)", "In these conditions, HTTP/3 often performs better due to its use of QUIC, which reduces head-of-line blocking."
    else:
        return "High latency (slow or distant network)", "HTTP/3 is generally more efficient over high-latency connections, thanks to improved congestion control and multiplexing."

# Measure latency
latency = get_latency()

# Predict and display
if latency is not None:
    input_data = pd.DataFrame([[latency]], columns=["latency"])
    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]
    
    protocol = "HTTP/3" if prediction == 1 else "HTTP/2"
    confidence = np.max(probabilities) * 100

    condition_label, condition_explanation = describe_condition(latency)

    print("--- Network Performance AI System ---")
    print(f"Current Latency: {latency:.2f} ms")
    print(f"{condition_label}")
    print(f"Recommended Protocol: {protocol}")
    print(f"Confidence Level: {confidence:.1f}%")
    
    print("\nExplanation:")
    print(f"{condition_explanation}")
    print(f"The AI model analyzed your latency value of {latency:.1f} ms and determined "
          f"that {protocol} is likely to deliver better performance under these conditions.")
else:
    print("Could not measure latency.")
