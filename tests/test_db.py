import os
from datetime import datetime, timedelta

from app import db


def test_alerting_logic_one_alert():

    start_datetime = datetime.utcnow()
    end_datetime = None

    log_entry = {
        "ip": "127.0.0.1",
        "user": "test_user",
        "method": "GET",
        "request_path": "blog/index.html",
        "section": "blog",
        "http_version": "1.1",
        "status_code": "200",
        "response_size": "1000",
        "referrer": "http://test.com/index.html",
        "user_agent": "Chrome",
    }
    # generate exactly 11 rps over 2 minutes
    threshold_rps = []
    for i in range(60 * 2):
        i_datetime = start_datetime + timedelta(seconds=i)
        end_datetime = i_datetime
        i_log_entry = log_entry.copy()
        i_log_entry["date"] = i_datetime
        for j in range(11):
            threshold_rps.append(i_log_entry)

    try:
        os.remove("log_analyzer.test.db")
    except OSError:
        pass
    db.connect_db("log_analyzer.test.db")
    db.setup_database()
    db.insert_log_entries(threshold_rps)
    db.create_alerts(end_datetime, 60 * 2, 10)
    alerts = db.find_alerts()
    assert len(alerts) == 1

def test_alerting_logic_zero_alert():

    start_datetime = datetime.utcnow()
    end_datetime = None

    log_entry = {
        "ip": "127.0.0.1",
        "user": "test_user",
        "method": "GET",
        "request_path": "blog/index.html",
        "section": "blog",
        "http_version": "1.1",
        "status_code": "200",
        "response_size": "1000",
        "referrer": "http://test.com/index.html",
        "user_agent": "Chrome",
    }
    # generate exactly 10 rps over 2 minutes
    threshold_rps = []
    for i in range(60 * 2):
        i_datetime = start_datetime + timedelta(seconds=i)
        end_datetime = i_datetime
        i_log_entry = log_entry.copy()
        i_log_entry["date"] = i_datetime
        for j in range(10):
            threshold_rps.append(i_log_entry)

    try:
        os.remove("log_analyzer.test.db")
    except OSError:
        pass
    db.connect_db("log_analyzer.test.db")
    db.setup_database()
    db.insert_log_entries(threshold_rps)
    db.create_alerts(end_datetime, 60 * 2, 10)
    alerts = db.find_alerts()
    assert len(alerts) == 0
