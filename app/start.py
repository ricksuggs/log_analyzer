import os
import re
import sqlite3
import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path

import pytz

from app import db
from app.config import config

date_format = "%d/%b/%Y:%H:%M:%S"
log_regex = r"(?P<ip>[(\d\.)]+) - (?P<user>.+) \[(?P<date>.*?) [+-](.*?)\] \"(?P<method>\w+) (?P<request_path>.*?) HTTP/(?P<http_version>.*?)\" (?P<status_code>\d+) (?P<response_size>[\-\d]+)"
compiled = re.compile(log_regex)


def run():
    db.setup_database()
    application_start_time = datetime.utcnow()

    while True:
        path = Path(config["log_file"])
        if path.is_file():
            break
        else:
            print(
                f"The configured log file {config['log_file']} doesn't exist, checking again in 5 seconds.."
            )
            time.sleep(5)

    with open(config["log_file"], "r") as file_:
        # move pointer to end of files
        # only process lines appended
        # since starting the script
        file_.seek(0, 2)

        try:
            while True:
                current_datetime = datetime.utcnow()
                insert_log_entries(file_.readlines())
                os.system("clear")
                print("Log Analyzer")
                print("-" * 40)
                print()
                print(
                    f"Application Start Time UTC: {application_start_time.isoformat()}"
                )
                print(f"Current Date/Time UTC: {current_datetime.isoformat()}")
                print("-" * 40)
                from_datetime = current_datetime - timedelta(
                    seconds=config["top_sections_seconds"]
                )
                print()
                print(
                    f"Top Sections (last {config['top_sections_seconds']} seconds)",
                    from_datetime.isoformat(),
                    "--",
                    current_datetime.isoformat(),
                )
                print("-" * 40)
                for result in find_top_sections(from_datetime, current_datetime):
                    section = result["section"]
                    section_count = result["section_count"]
                    print(
                        section,
                        " " * (40 - len(str(section)) - len(str(section_count))),
                        section_count,
                        sep="",
                    )
                print("-" * 40)
                print()
                print("Alerts")
                print("-" * 40)
                for result in find_alerts():
                    if result["recovered"] == 1:
                        print("Alert recovered")
                    print(
                        "High traffic generated an alert - hits =",
                        result["hits"],
                        "triggered at",
                        result["create_datetime"],
                    )
                print("-" * 40)
                print()
                if config["purge_log_entries_seconds"]:
                    purge_log_entries(
                        current_datetime
                        - timedelta(seconds=config["purge_log_entries_seconds"])
                    )
                time.sleep(config["top_sections_seconds"])
        except KeyboardInterrupt:
            db.close_connection()


def insert_log_entries(lines):
    try:
        parsed_lines = []
        for line in lines:
            parsed_line = parse_line(line)
            if not parsed_line:
                print("Parser failed to parse line: ", line)
                time.sleep(10)
            else:
                parsed_lines.append(parsed_line)
        db.insert_log_entries(parsed_lines)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        print("Unexpected error:", sys.exc_info()[0])
        traceback.print_exc()


def parse_line(line):
    line = line.rstrip("\n")
    match = compiled.match(line)
    if not match:
        return None
    data = match.groupdict()
    unaware_datetime = datetime.strptime(data["date"], date_format)
    data["date"] = pytz.utc.localize(unaware_datetime)
    data["section"] = data["request_path"].split("/")[1]
    return data


def find_alerts():
    try:
        db.create_alerts(
            datetime.utcnow(),
            config["alert_range_seconds"],
            config["threshold_average_rps"],
        )
        alerts = db.find_alerts()
        if not alerts:
            print("No alerts found")
            return []
        return alerts
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        print("Unexpected error:", sys.exc_info()[0])
        traceback.print_exc()


def find_top_sections(from_datetime: datetime, to_datetime: datetime):
    try:
        top_sections = db.find_top_sections(from_datetime, to_datetime)
        if not top_sections:
            print(
                f"No log entries from the past {config['top_sections_seconds']} seconds."
            )
            print(f"Timestamp in log entry must match current time in UTC.")
            return []
        return top_sections
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        print("Unexpected error:", sys.exc_info()[0])
        traceback.print_exc()


def purge_log_entries(to_datetime):
    try:
        db.purge_log_entries(to_datetime)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        print("Unexpected error:", sys.exc_info()[0])
        traceback.print_exc()


if __name__ == "__main__":
    run()
