#!/usr/bin/python3

#Modules
import sys, os, subprocess

#Global variables
exit_code = 0

#Clear the screen
subprocess.run("clear")

#Get the log file name
try:
    log_path = sys.argv[1]
except IndexError:
    print("Usage: python3 log_analyzer.py <log_file>")
    sys.exit(1)

if not os.path.exists(log_path):
    print(f"File {log_path} does not exist")
    sys.exit(1)

def count_lines(log_path):
    total_lines = 0
    total_errors = 0
    total_warnings = 0
    with open(log_path, "r") as log_file:
        for line in log_file:
            total_lines += 1
            if "error" in line:
                total_errors += 1
            if "warning" in line:
                total_warnings += 1

    return total_lines, total_errors, total_warnings

#Count lines, errors and warnings
total_lines, total_errors, total_warnings = count_lines(log_path)

print("=== LOG ANALYZER ===")
print(f"File: {log_path}")
print(f"Total lines: {total_lines}")
print(f"Errors: {total_errors}")
print(f"Warnings: {total_warnings}")

sys.exit(exit_code)