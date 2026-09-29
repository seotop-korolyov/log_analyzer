#!/usr/bin/python3

#Modules
import sys, os, subprocess

#Global variables
exit_code = 0

#Clear the screen
subprocess.run(["clear"])

#Get the log file name
try:
    log_path = sys.argv[1]
except IndexError:
    print("Usage: python3 log_analyzer.py <log_file>")
    sys.exit(1)

if not os.path.exists(log_path):
    print(f"File {log_path} does not exist")
    sys.exit(1)

def log_analyzer(log_path):
    total_lines = 0
    total_errors = 0
    total_warnings = 0
    error_messages = {}
    errors_by_service = {}
    malformed_lines = 0
    with open(log_path, "r") as log_file:
        for line in log_file:
            line_lower = line.lower()
            total_lines += 1
            if "error" in line_lower:
                total_errors += 1
                error_line = line.strip().split()

                #Servcie error
                if len(error_line) < 6:
                    malformed_lines += 1
                    continue
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
    malformed_lines = log_analyzer(log_path)
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
print(f"Total lines: {total_lines}")
print(f"Errors: {total_errors}, rate: {error_rate:.2f}%")
print(f"Warnings: {total_warnings}")
print(f"Malformed_lines: {malformed_lines}")
print("=== ERRORS [TOP-3] ===")
error_sorted = sorted(
    error_messages.items(), key=lambda item:item[1], reverse=True
    )
for error, count in error_sorted[:3]:
    print(f"{error}: {count}")

print("=== ERRORS BY SERVICES [TOP-3] ===")
errors_by_service_sorted = sorted(
    errors_by_service.items(), key=lambda item:item[1], reverse=True
)
for error, count in errors_by_service_sorted[:3]:
    print(f"{error}: {count}")

sys.exit(exit_code)