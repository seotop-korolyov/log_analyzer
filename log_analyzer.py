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
    total_errors = 0
    total_warnings = 0
    error_messages = {}
    errors_by_service = {}
    malformed_lines = 0
    with open(log_path, "r") as log_file:
        for line in log_file:
            #Parse the line
            parsed = parse_log_line(line)

            if parsed is None:
                malformed_lines += 1
                continue

            level, service_error, error_message = parsed
    
            if service is not None and service_error != service:
                continue
            if level_filter is not None and level != level_filter:
                continue

            total_lines += 1

            #Count errors
            if level == "error" or level_filter == "error":
                #Tottal errors
                total_errors += 1

                #Service errors
                if service_error not in errors_by_service:
                    errors_by_service[service_error] = 1
                else:
                    errors_by_service[service_error] += 1

                #Error message
                if error_message not in error_messages:
                    error_messages[error_message] = 1
                else:
                    error_messages[error_message] += 1

            #Count warnings
            if level == "warning" or level_filter == "warning":
                total_warnings += 1

    return total_lines, \
            total_errors, \
            total_warnings, \
            error_messages, \
            errors_by_service, \
            malformed_lines

#Parce log_line
def parse_log_line(line):
    error_line = line.strip().split()
    
    # Check whether the error_line is valid
    if len(error_line) < 6:
        return None
    
    level = error_line[2].lower()
    service_error = error_line[3].strip("[]")
    error_message = " ".join(error_line[5:])
    
    return level, service_error, error_message



#Count lines, errors and warnings
try:
    total_lines, \
    total_errors, \
    total_warnings, \
    error_messages, \
    errors_by_service, \
    malformed_lines = log_analyzer(log_path, service, level_filter)
except PermissionError:
    print(f"Error: permission denied: {log_path}")
    sys.exit(1)

#Count error rate
if total_lines > 0:
    error_rate = ( total_errors / total_lines ) * 100
else:
    error_rate = 0

print("=== LOG ANALYZER ===")
print(f"File: {log_path}")
if service:
    print(f"Service: {service}")
print(f"Total lines: {total_lines}")
if total_errors > 0:
    print(f"Errors: {total_errors}, rate: {error_rate:.2f}%")
if total_warnings > 0:
    print(f"Warnings: {total_warnings}")
print(f"Malformed lines: {malformed_lines} \n")
print(f"=== ERRORS [TOP-{top}] ===")
error_sorted = sorted(
    error_messages.items(), key=lambda item:item[1], reverse=True
    )
for error, count in error_sorted[:top]:
    print(f"{error}: {count}")
print("\n")
print(f"=== ERRORS BY SERVICES [TOP-{top}] ===")
errors_by_service_sorted = sorted(
    errors_by_service.items(), key=lambda item:item[1], reverse=True
)
for error, count in errors_by_service_sorted[:top]:
    print(f"{error}: {count}")
print("\n\n")

sys.exit(exit_code)