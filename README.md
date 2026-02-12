# PubNub-device-logging

## Details
Captures and ships logs from device, then collects on centralized logging system

`log_cap.py`
* Used by services / apps to write logs locally
* Not required is other mechanisms are used to rwite logs
* Logs are created in `log/` dir
* Log files created with naming convention of `{$processname}.log`
* The following code will need to be added to any python apps
```
from log_cap import start_logging
start_logging(os.path.basename(__file__))
```

`log_shipper.py`
* Will read all files from within the configured `log/` directory, then Publish the messages to PubNub
* Name of logfile the log lines were read from is included in the message sent to PubNub
* Deletes log lines from local file after sent to PubNub

`log_collector.py`
* Subscribes to PubNub logging channel
* Reads message data to determine name of log file the message should be appended to
* When started, will first check for existing messages, write to local files, then delete the Message from PubNub
* Receives messages as they are Published, writes to local files, then deleted from PubNub
* Logs save to configurable `central_logs/` directory

`dashboard.html`
* Warning, this is not a secure method of displaying logs
* This is rudimentary, and only intended for demo purposes
* Revision of the dashboad from [PubNub-device-monitoring](https://github.com/krsboone/PubNub-device-monitoring)
* Pulls and displays data from configurable log files, within the `central_logs/` directory
* Assumes that log files are accessible from same web server - does not access directly through filesystem

## Config

Replace
```
publishKey: "pub-key-here"
subscribeKey: "sub-key-here"
```

with your pub/sub keys

Install PubNub Python SDK
`pip install 'pubnub>=10.6.1'`
https://www.pubnub.com/docs/sdks/python


## Todo
1. Create "browser logging" version of this demo
2. Give broader consideration to dashboard security
3. Ability to toggle on/off the device availability mornitoring section of the dashboard
