"""
a listener to provide results from locust tests in a JMeter compatible format
and thereby allow JMeter users with existing reporting solutions to transition more easily
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from time import time

from locust.runners import WorkerRunner


class JmeterListener:
    """
    create an intance of the listener at the start of a test
    to create a JMeter style results file
    different formats can be chosen in initialisation
    (field_delimiter and timestamp_format)
    and the number of results to send to a log file at a time (flush_size)
    """

    # holds results until processed
    csv_results = []

    def __init__(
        self,
        env,
        testplan="testplanname",
        field_delimiter=",",
        timestamp_format="%Y/%m/%d %H:%M:%S",
        flush_size=100,
        results_filename=None,
    ):
        self.env = env
        self.runner = self.env.runner
        self.is_worker_runner = isinstance(self.env.runner, WorkerRunner)

        self.testplan = testplan
        # default JMeter field and row delimiters
        self.field_delimiter = field_delimiter
        # a timestamp format, others could be added...
        self.timestamp_format = timestamp_format
        # how many records should be held before flushing to disk
        self.flush_size = flush_size
        if not results_filename:
            # results filename format
            self.results_filename = f"results_{datetime.fromtimestamp(time()).strftime('%Y_%m_%d_%H_%M_%S')}.csv"
            self.results_filename = os.path.join(
                os.path.dirname(env.parsed_options.csv_prefix),
                "jmeter",
                f"results_{os.path.basename(env.parsed_options.csv_prefix)}.csv",
            )
        else:
            self.results_filename = results_filename

        # fields set by default in jmeter
        self.csv_headers = [
            "timeStamp",
            "elapsed",
            "label",
            "responseCode",
            "responseMessage",
            "threadName",
            "dataType",
            "success",
            "failureMessage",
            "bytes",
            "sentBytes",
            "grpThreads",
            "allThreads",
            "Latency",
            "IdleTime",
            "Connect",
        ]

        self.user_count = 0
        self.testplan = ""
        events = self.env.events
        if self.is_worker_runner:
            events.report_to_master.add_listener(self._report_to_master)
        else:
            self.results_file = self._create_results_log()
            events.quitting.add_listener(self._write_final_log)
            events.worker_report.add_listener(self._worker_report)

        events.request.add_listener(self._request)

    def _create_results_log(self):
        filename = Path(self.results_filename)
        filename.parent.mkdir(exist_ok=True, parents=True)
        filename.touch(exist_ok=True)
        results_file = open(filename, "w")
        self.cvs_writer = csv.writer(results_file, delimiter=self.field_delimiter, quotechar='"')
        self.cvs_writer.writerow(self.csv_headers)
        results_file.flush()
        return results_file

    def _flush_to_log(self):
        self.cvs_writer.writerows(self.csv_results)
        self.results_file.flush()
        self.csv_results = []

    def _write_final_log(self, **kwargs):
        self.cvs_writer.writerows(self.csv_results)
        self.results_file.close()

    def add_result(self, success, _request_type, name, response_time, response_length, exception, **kw):
        timestamp = datetime.fromtimestamp(time()).strftime(self.timestamp_format)
        response_message = "OK" if success == "true" else "KO"
        # check to see if the additional fields have been populated. If not, set to a default value
        status_code = kw["status_code"] if "status_code" in kw else "0"
        thread_name = self.testplan
        data_type = kw["data_type"] if "data_type" in kw else "unknown"
        bytes_sent = kw["bytes_sent"] if "bytes_sent" in kw else "0"
        group_threads = str(self.runner.user_count)
        all_threads = str(self.runner.user_count)
        latency = kw["latency"] if "latency" in kw else "0"
        idle_time = kw["idle_time"] if "idle_time" in kw else "0"
        connect = kw["connect"] if "connect" in kw else "0"
        row = [
            timestamp,
            str(round(response_time)),
            name,
            str(status_code),
            response_message,
            thread_name,
            data_type,
            success,
            exception,
            str(response_length),
            bytes_sent,
            str(group_threads),
            str(all_threads),
            latency,
            idle_time,
            connect,
        ]
        self.csv_results.append(row)
        if len(self.csv_results) >= self.flush_size and not self.is_worker_runner:
            self._flush_to_log()

    def _request(self, request_type, name, response_time, response_length, exception, **kw):
        self.add_result("false" if exception else "true", request_type, name, response_time, response_length, str(exception), **kw)

    def _report_to_master(self, data, **kwargs):
        data["csv_results"] = self.csv_results
        self.csv_results = []

    def _worker_report(self, data, **kwargs):
        self.csv_results += data["csv_results"]
        if len(self.csv_results) >= self.flush_size:
            self._flush_to_log()
