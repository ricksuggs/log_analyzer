# config
config = {
    # number of seconds back to query for tops sections
    "top_sections_seconds": 10,
    # average requests per second alert threshold
    "threshold_average_rps": 10,
    # average requests per second alert range, default 2 minutes
    "alert_range_seconds": 60 * 2,
    # log file to watch
    "log_file": "/tmp/access.log",
    # purge the log_entries from configured number of hours before current datetime, default 1 hr
    "purge_log_entries_seconds": 60 * 60,
    # sql connection string
    "sql_connection_string": "log_analyzer.db",
}
