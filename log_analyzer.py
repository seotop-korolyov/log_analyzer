#!/usr/bin/python3

#Modules
import sys, os

#Global variables
exit_code = 0

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
    with open(log_path, "r") as log_file:
        total_lines = 0
        for line in log_file:
            total_lines += 1
    return total_lines

print("=== LOG ANALYZER ===")
print(f"File: {log_path}")
print(f"Total lines: {count_lines(log_path)}")
print(f"Errors: ")
print(f"Warnings:")

sys.exit(exit_code)