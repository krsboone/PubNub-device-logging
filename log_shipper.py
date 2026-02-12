import os
import time
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

# 1. PubNub Setup
pnconfig = PNConfiguration()
pnconfig.publish_key = 'pub-key-here'
pnconfig.subscribe_key = 'sub-key-here'
pnconfig.user_id = "log_shipper_service"
pubnub = PubNub(pnconfig)

LOG_DIR = "log"
PUB_CHANNEL = "logging"

def ship_logs():
    if not os.path.exists(LOG_DIR):
        print(f"Waiting for {LOG_DIR} directory...")
        return

    # Scan all files in the log directory
    for filename in os.listdir(LOG_DIR):
        if filename.endswith(".log"):
            file_path = os.path.join(LOG_DIR, filename)

            # Read lines and clear file
            try:
                with open(file_path, "r+", encoding="utf-8") as f:
                    lines = f.readlines()

                    if not lines:
                        continue

                    print(f"--- Shipping {len(lines)} lines from {filename} ---")

                    for line in lines:
                        clean_line = line.strip()
                        if not clean_line:
                            continue

                        # Send to PubNub
                        pubnub.publish().channel(PUB_CHANNEL).message({
                            "source": filename,
                            "log": clean_line,
                            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                        }).sync()

                    # Clear the file after successful send
                    f.seek(0)
                    f.truncate()

            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    print(f"--- Log Shipper Active: Monitoring {LOG_DIR} ---")
    while True:
        ship_logs()
        time.sleep(5) # Adjust frequency as needed
