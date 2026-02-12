import os
import datetime
import time
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback

# 1. PubNub Setup
pnconfig = PNConfiguration()
pnconfig.publish_key = 'pub-key-here'
pnconfig.subscribe_key = 'sub-key-here'
pnconfig.user_id = "central_log_collector"
pubnub = PubNub(pnconfig)

CENTRAL_DIR = "central_logs"
PUB_CHANNEL = "logging"
CLEANUP_LOG = os.path.join(CENTRAL_DIR, "message_cleanup.log")

if not os.path.exists(CENTRAL_DIR):
    os.makedirs(CENTRAL_DIR)

def process_log_entry(msg, timetoken):
    """Core logic to save file and purge cloud record"""
    source_file = msg.get("source", "unknown.log")
    log_content = msg.get("log", "")
    file_path = os.path.join(CENTRAL_DIR, source_file)

    try:
        # 1. Save locally
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{log_content}\n")

        # 2. Delete from PubNub
        envelope = pubnub.delete_messages() \
            .channel(PUB_CHANNEL) \
            .start(0) \
            .end(timetoken) \
            .sync()

        # 3. Log cleanup
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(CLEANUP_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] PURGE: {source_file} @ {timetoken} | Status: {envelope.status}\n")

        return True
    except Exception as e:
        print(f"❌ Processing Error: {e}")
        return False

def sync_backlog():
    """Fetch any messages missed while offline"""
    print(f"--- Syncing backlog for {PUB_CHANNEL}... ---")
    try:
        # .sync() returns an envelope. Need the .result from inside it.
        envelope = pubnub.fetch_messages().channels([PUB_CHANNEL]).count(100).sync()

        # Access the result attribute
        result = envelope.result

        # Check if the result has channels and if specific channel is there
        if result and result.channels and PUB_CHANNEL in result.channels:
            messages = result.channels[PUB_CHANNEL]

            if not messages:
                print("✨ No backlog found. Channel is clean.")
                return

            print(f"📥 Found {len(messages)} missed messages. Processing...")
            for item in messages:
                # item.message is the payload, item.timetoken is the unique ID
                process_log_entry(item.message, item.timetoken)

            print("✅ Backlog sync complete.")
        else:
            print("✨ No historical messages detected in the result.")

    except Exception as e:
        print(f"❌ Sync Failed: {e}")

class CollectorCallback(SubscribeCallback):
    def message(self, pubnub, event):
        print(f"📨 Real-time message received from {event.message.get('source')}")
        process_log_entry(event.message, event.timetoken)

# --- EXECUTION FLOW ---

# 1. Clear the backlog first
import asyncio
# Use sync() for simplicity in this script pattern
sync_backlog()

# 2. Start real-time listener
pubnub.add_listener(CollectorCallback())
pubnub.subscribe().channels([PUB_CHANNEL]).execute()

print(f"--- Central Collector Fully Synchronized & Active ---")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nCollector shutting down.")
