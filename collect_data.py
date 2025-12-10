import subprocess
import csv
import time
import platform
import re


TEST_URL = "https://cloudflare.com"   # Works with HTTP/3
OUTPUT_FILE = "network_data.csv"
ITERATIONS = 10

# Detect OS (Windows vs Linux/Mac)
IS_WINDOWS = platform.system().lower().startswith("win")

#Run ping to estimate latency

def get_latency(host="8.8.8.8"):
    try:
        # Windows vs Linux ping command
        cmd = ["ping", "-n", "3", host] if IS_WINDOWS else ["ping", "-c", "3", host]
        output = subprocess.check_output(cmd, universal_newlines=True)

        if IS_WINDOWS:
            # Extract average from "Average = XXms"
            match = re.search(r"Average = (\d+)ms", output)
            if match:
                return float(match.group(1))
        else:
            # Linux/Mac format: "avg = 24.6"
            avg_line = [line for line in output.split("\n") if "avg" in line]
            if avg_line:
                avg_time = avg_line[0].split("/")[4]
                return float(avg_time)
    except Exception as e:
        print("Ping error:", e)
    return None

#Run curl test (returns total time)

def test_protocol(protocol_flag):
    try:
        # Use the full path to the working curl binary 
        cmd = [
            r"C:\curl\curl-8.17.0_4-win64-mingw\bin\curl.exe",
            "-s",
            "-o", "nul" if IS_WINDOWS else "/dev/null",  # discard output
            "-w", "%{time_total}",                      # print only total time
            protocol_flag,
            TEST_URL
        ]

        # Run the curl command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()

        # Debug: show raw output
        print(f"[DEBUG] Raw curl output ({protocol_flag}): '{output}'")

        # Extract the first floating-point number from output
        match = re.search(r"([0-9]*\.[0-9]+)", output)
        if match:
            return float(match.group(1))
        else:
            print(f"[WARN] No numeric match found in output for {protocol_flag}")
            if result.stderr.strip():
                print(f"[INFO] curl stderr ({protocol_flag}): {result.stderr.strip()}")

    except subprocess.TimeoutExpired:
        print(f"[ERROR] Timeout expired while testing {protocol_flag}")
    except FileNotFoundError:
        print(f"[ERROR] curl binary not found at specified path: {cmd[0]}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in test_protocol({protocol_flag}): {e}")

    return None

# Main testing loop

with open(OUTPUT_FILE, "w", newline="") as csvfile:
    fieldnames = ["latency", "protocol", "time"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(ITERATIONS):
        print(f"\nIteration {i+1}/{ITERATIONS}")
        latency = get_latency()

        t_http2 = test_protocol("--http2")
        t_http3 = test_protocol("--http3")

        if latency and t_http2 and t_http3:
            writer.writerow({"latency": latency, "protocol": "HTTP/2", "time": t_http2})
            writer.writerow({"latency": latency, "protocol": "HTTP/3", "time": t_http3})
            print(f"Latency={latency} ms | HTTP/2={t_http2}s | HTTP/3={t_http3}s")
        else:
            print("Skipped iteration")

        time.sleep(2)

print(f"\nData collection complete. Saved to {OUTPUT_FILE}")
