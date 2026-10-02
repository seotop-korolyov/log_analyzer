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
args = parser.parse_args()

#Parameters
log_path = args.log_path
top = args.top
service = args.service

#Checking --top parametr
if top <= 0:
    parser.error("--top must be a positive integer")

if not os.path.exists(log_path):
    print(f"File {log_path} does not exist")
    sys.exit(1)

def log_analyzer(log_path, service):
    total_lines = 0
    total_errors = 0
    total_warnings = 0
    error_messages = {}
    errors_by_service = {}
    malformed_lines = 0
    with open(log_path, "r") as log_file:
        for line in log_file:
            line_lower = line.lower()
            error_line = line.strip().split()
            
            #Check wether the error_line is OK
            if len(error_line) < 6:
                malformed_lines += 1
                continue
            else:
                service_error = error_line[3].strip("[]")

            if service is not None:
                if service_error != service:
                    continue
            total_lines += 1

            #Count Errors
            if "error" in line_lower:
                #Tottal lines
                total_errors += 1

                #Servcie error
                service_error = error_line[3].strip("[]")
                if service_error not in errors_by_service:
                    errors_by_service[service_error] = 1
                else:
                    errors_by_service[service_error] += 1

                #Error message
                error_line = " ".join(error_line[5:])
                if error_line not in error_messages:
                    error_messages[error_line] = 1
                else:
                    error_messages[error_line] += 1

            #Count Warnings
            if "warning" in line_lower:
                total_warnings += 1

    return total_lines, \
            total_errors, \
            total_warnings, \
            error_messages, \
            errors_by_service, \
            malformed_lines

#Count lines, errors and warnings
try:
    total_lines, \
    total_errors, \
    total_warnings, \
    error_messages, \
    errors_by_service, \
    malformed_lines = log_analyzer(log_path, service)
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
print(f"Errors: {total_errors}, rate: {error_rate:.2f}%")
print(f"Warnings: {total_warnings}")
print(f"Malformed lines: {malformed_lines}")
print(f"=== ERRORS [TOP-{top}] ===")
error_sorted = sorted(
    error_messages.items(), key=lambda item:item[1], reverse=True
    )
for error, count in error_sorted[:top]:
    print(f"{error}: {count}")

print(f"=== ERRORS BY SERVICES [TOP-{top}] ===")
errors_by_service_sorted = sorted(
    errors_by_service.items(), key=lambda item:item[1], reverse=True
)
for error, count in errors_by_service_sorted[:top]:
    print(f"{error}: {count}")

sys.exit(exit_code)