Log Analyzer

This project requires Python 3.6

Please note: 

* Timestamps in log file must match up with current datetime in *UTC* while runnning the app (`datetime.datetime.utcnow()`)
* The app will only process new lines added to configured log file after starting. It will not process pre existing lines.
* Install virtual environment: `python -m venv .venv`
* Activate virtual environment: `source .venv/bin/activate`
* Install dependencies: `pip3 install --editable .`
* Build project: `python setup.py develop`
* Run tests: `python setup.py pytest`
* Run mock logging: `python ./mock/mock_activity.py`
* Run log_analyzer app: `python ./app/start.py`
* Configuration: See app/config.py
* Build docker: sudo docker build -t log_analyzer .
* Run docker: sudo docker run -it -v /tmp:/tmp log_analyzer python3 ./app/start.py

