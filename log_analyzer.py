#!/usr/bin/python3

#Modules
import sys, os, subprocess, argparse

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
args = parser.parse_args()

#Parameters
log_path = args.log_path
top = args.top
service = args.service
level_filter = args.level

#Checking --top parametr
if top <= 0:
    parser.error("--top must be a positive integer")

if not os.path.exists(log_path):
    print(f"File {log_path} does not exist")
    sys.exit(1)

def log_analyzer(log_path, service, level_filter):
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

            level, service_name, message = parsed

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
    
    level = log_line[2].lower()
    service_name = log_line[3].strip("[]")
    message = " ".join(log_line[5:])
    
    return level, service_name, message

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

#Output
def output(level, by_service, top, messages):
    print(f"=== {level.upper()} [TOP-{top}] ===")
    level_sorted = sorted(
        messages.items(), key=lambda item:item[1], reverse=True
    )
    for message, count in level_sorted[:top]:
        print(f"{message}: {count}")
    print("\n")
    print(f"=== {level.upper()} BY SERVICES [TOP-{top}] ===")
    by_service_sorted = sorted(
        by_service.items(), key=lambda item:item[1], reverse=True
    )
    for service_name, count in by_service_sorted[:top]:
        print(f"{service_name}: {count}")
    print("\n")


#Count lines, errors and warnings
try:
    total_lines, \
    malformed_lines, \
    stats = log_analyzer(log_path, service, level_filter)
except PermissionError:
    print(f"Error: permission denied: {log_path}")
    sys.exit(1)

#Count error rate
if total_lines > 0:
    error_rate = ( stats["error"]['count'] / total_lines ) * 100
else:
    error_rate = 0

#Print out
print("=== LOG ANALYZER ===")
print(f"File: {log_path}")
if service:
    print(f"Service: {service}")
if level_filter:
    print(f"Level: {level_filter}")
print(f"Total lines: {total_lines}")

if level_filter is None or level_filter == "error":
    print(f"Errors: {stats['error']['count']}, rate: {error_rate:.2f}%")

if level_filter is None or level_filter == "warning":
    print(f"Warnings: {stats['warning']['count']}")

print(f"Malformed lines: {malformed_lines} \n")

#Error section
if level_filter is None or level_filter == "error":
    output("error", stats["error"]["services"], top, stats["error"]["messages"])
#Warning section
if level_filter is None or level_filter == "warning":
    output("warning", stats["warning"]["services"], top, stats["warning"]["messages"])
#Info
if level_filter is None or level_filter == "info":
    output("info", stats["info"]["services"], top, stats["info"]["messages"])
#Debug
if level_filter is None or level_filter == "debug":
    output("debug", stats["debug"]["services"], top, stats["debug"]["messages"])

print("\n\n")

#Exit code
sys.exit(exit_code)