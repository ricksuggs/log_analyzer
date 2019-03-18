import time
import datetime
import os

try:
    with open("mock/sample_http_access_log.1.log", "r") as sample_log:
        with open("/tmp/access.log", "a") as mock_log:
            for line in sample_log:
                current_datetime = datetime.datetime.utcnow()
                formatted_datetime = datetime.date.strftime(
                    current_datetime, "%d/%b/%Y:%H:%M:%S"
                )
                mock_log.writelines(
                    [line.replace("{timestamp}", f"[{formatted_datetime} +0000]")]
                )
                mock_log.flush()
                os.fsync(mock_log.fileno())
                # time.sleep(1)
except KeyboardInterrupt:
    pass
