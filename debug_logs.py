import boto3
import os
import time

# Load .env manually for local creds
try:
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
except Exception as e:
    pass

region = os.environ.get('AWS_REGION', 'us-east-2')
group_name = '/aws/lambda/weight-planner-function'

try:
    client = boto3.client('logs', region_name=region)
    
    print(f"Fetching ALL logs from {group_name} (Last 10 mins)...")
    
    # Time in ms (Last 10 minutes)
    start_time = int((time.time() - 600) * 1000)
    
    response = client.filter_log_events(
        logGroupName=group_name,
        startTime=start_time,
        limit=100, # Get more events
        interleaved=True
    )
    
    events = response['events']
    if not events:
        print("No logs found in the last 10 minutes.")
    else:
        print(f"\nFound {len(events)} events. Dumping non-system messages:\n")
        print("-" * 50)
        for event in events:
            msg = event['message'].strip()
            # Filter out standard Lambda platform messages to highlight errors
            if not msg.startswith(("START RequestId", "END RequestId", "REPORT RequestId")):
                print(f"[{event['timestamp']}] {msg}")
            # Identify specific errors in REPORT lines if needed (e.g. Init Duration)
            elif "Init Duration" in msg:
                 print(f"[{event['timestamp']}] {msg}")
        print("-" * 50)

except Exception as e:
    print(f"Error fetching logs: {e}")
