#!/usr/bin/python3
import os, re, subprocess
from time import strftime,localtime

def get_timestamp():
    return strftime("%H-%M-%S-%d-%m-%Y", localtime())

def log_cmd_results(cmd, log):
    log.write("Return Code: " + str(cmd.returncode) + "\n")

    log.write("STDOUT\n")
    log.write("==================================================\n")
    log.write(str(cmd.stdout) + "\n")

    log.write("STDERR\n")
    log.write("==================================================\n")
    log.write(str(cmd.stderr) + "\n")

    log.write("\n")
