#!/usr/bin/python3

#Modules
import sys, os, subprocess, argparse
from datetime import datetime

#Global variables
exit_code = 0

#Clear the screen
subprocess.run(["clear"])

#Parse arguments
parser = argparse.ArgumentParser(
    description="Analyze application logs and report errors and warnings."
)
#log_path
parser.add_argument(
    "log_path",
    help="Path to the log file")
#--top
parser.add_argument(
    "--top", "-t",
    type=int,
    default=5,
    help="Number of top errors and services to display"
)
#--service
parser.add_argument(
    "--service", "-s",
    type=str,
    help="Analyze only the specified service",
    default=None
)
#--level
parser.add_argument(
    "--level", "-l",
    type=str,
    choices=["error", "warning", "info", "debug"],
    default=None,
    help="Choose a level from 'error', 'warning', 'info', or 'debug'"
)
#--since
parser.add_argument(
    "--since",
    type=str,
    default=None,
    help="Analyze log entries from this time (YYYY-MM-DD HH:MM:SS)"    
)
args = parser.parse_args()

#Parameters
log_path = args.log_path
top = args.top
service = args.service
level_filter = args.level
since = args.since

#Checking --top parametr
if top <= 0:
    parser.error("--top must be a positive integer")

if not os.path.exists(log_path):
    print(f"File {log_path} does not exist")
    sys.exit(1)

def log_analyzer(log_path, service, level_filter, since):
    total_lines = 0
    malformed_lines = 0
    stats = {
        "error": {
            "count": 0,
            "messages": {},
            "services": {}
        },
        "warning": {
                    "count": 0,
                    "messages": {},
                    "services": {}
        },
        "info": {
                    "count": 0,
                    "messages": {},
                    "services": {}
        },
        "debug": {
                    "count": 0,
                    "messages": {},
                    "services": {}
        }
    }
    with open(log_path, "r") as log_file:
        for line in log_file:
            #Parse the line
            parsed = parse_log_line(line)

            if parsed is None:
                malformed_lines += 1
                continue

            timestamp, level, service_name, message = parsed
            if since is not None and timestamp < since:
                continue

            if service is not None and service_name != service:
                continue

            total_lines += 1
        
            if level_filter is not None and level != level_filter:
                continue

            #Count statistic
            if level in stats:
                update_stats(stats, level, service_name, message)

    return total_lines, \
            malformed_lines, \
            stats

#Parce log_line
def parse_log_line(line):
    log_line = line.strip().split()
    
    # Check whether the error_line is valid
    if len(log_line) < 6:
        return None

    try:
        timestamp_string = log_line[0] + " " + log_line[1]
        timestamp = datetime.strptime(timestamp_string, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    
    level = log_line[2].lower()
    service_name = log_line[3].strip("[]")
    message = " ".join(log_line[5:])
    
    return timestamp, level, service_name, message

#Stat
def update_stats(stats, level, service_name, message):
    stats[level]["count"] += 1

    #Service errors
    if service_name not in stats[level]["services"]:
        stats[level]["services"][service_name] = 1
    else:
        stats[level]["services"][service_name] += 1

    #Error message
    if message not in stats[level]["messages"]:
        stats[level]["messages"][message] = 1
    else:
        stats[level]["messages"][message] += 1

#Count error rate
def rate(stats, level, total_lines):
    if total_lines > 0:
        rate_number = ( stats[level]['count'] / total_lines ) * 100
    else:
        rate_number = 0
    return rate_number

#Output
def output(level, stats, top):
    print(f"=== {level.upper()} [TOP-{top}] ===")
    level_sorted = sorted(
        stats[level]["messages"].items(), key=lambda item:item[1], reverse=True
    )
    for message, count in level_sorted[:top]:
        print(f"{message}: {count}")
    print("\n")
    print(f"=== {level.upper()} BY SERVICES [TOP-{top}] ===")
    by_service_sorted = sorted(
        stats[level]["services"].items(), key=lambda item:item[1], reverse=True
    )
    for service_name, count in by_service_sorted[:top]:
        print(f"{service_name}: {count}")
    print("\n")

#Convert datetime
if args.since is not None:
    try:
        since = datetime.strptime(
            args.since,
            "%Y-%m-%d %H:%M:%S"
        )
    except ValueError:
        parser.error("--since must use format YYYY-MM-DD HH:MM:SS")

#Count lines, errors and warnings
try:
    total_lines, \
    malformed_lines, \
    stats = log_analyzer(log_path, service, level_filter, since)
except PermissionError:
    print(f"Error: permission denied: {log_path}")
    sys.exit(1)

#Print out
print("=== LOG ANALYZER ===")
print(f"File: {log_path}")
if service:
    print(f"Service: {service}")
if level_filter:
    print(f"Level: {level_filter}")
print(f"Total lines: {total_lines}")

#Output numbers of levels
for level in stats:
    if level_filter is not None and level != level_filter:
        continue
    print(f"{level.capitalize()} lines: {stats[level]['count']}, rate: {rate(stats, level, total_lines):.2f}%")

print(f"Malformed lines: {malformed_lines} \n")

#Output by level_filter
for level in stats:
    if level_filter is not None and level != level_filter:
        continue
    output(level, stats, top)

print("\n\n")

#Exit code
sys.exit(exit_code)