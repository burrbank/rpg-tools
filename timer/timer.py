#!/bin/python
import argparse
from datetime import datetime, timedelta
from math import floor
import sys
from time import sleep

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", "-n", type=str, default="Counter")
    parser.add_argument("--minutes", "-m", type=int, default=1)
    return parser.parse_args(args)
    

def main():
    args = parse_args(sys.argv[1:])
    
    start_time = datetime.now()
    
    while True:
        current_time = datetime.now()
        time_diff = current_time - start_time
        
        intervals = time_diff / timedelta(minutes=args.minutes)
        intervals = floor(intervals)
        
        print(f"{args.name} | {args.minutes} min interval | {intervals} intervals \r", end='')

        sleep(10)

if __name__ == "__main__":
    main()