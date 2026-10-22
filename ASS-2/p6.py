import sys
from collections import deque

def parse_time(time_str):
    parts = time_str.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0

def detect_log_anomalies():
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return

    first_line = input_data[0].split()
    X = int(first_line[0])
    T = int(first_line[1])
    
    n = int(input_data[1])
    
    user_failures = {}
    suspicious_users = {}
    
    for i in range(2, 2 + n):
        if i >= len(input_data):
            break
        
        line = input_data[i].strip()
        if not line:
            continue
            
        parts = line.split()
        if len(parts) < 4:
            continue
            
        timestamp_str, user, ip, status = parts[0], parts[1], parts[2], parts[3].upper()
        current_time = parse_time(timestamp_str)
        
        if user not in user_failures:
            user_failures[user] = deque()
            
        failures_queue = user_failures[user]
        
        while failures_queue and (current_time - failures_queue[0][0] > T):
            failures_queue.popleft()
            
        if status == "FAIL":
            failures_queue.append((current_time, ip))
        elif status == "SUCCESS":
            if len(failures_queue) >= X:
                distinct_ip_failure_exists = any(fail_ip != ip for _, fail_ip in failures_queue)
                if distinct_ip_failure_exists:
                    if user not in suspicious_users:
                        suspicious_users[user] = timestamp_str
                        
    for user in sorted(suspicious_users.keys()):
        print(f"{user} {suspicious_users[user]}")

if __name__ == "__main__":
    detect_log_anomalies()
