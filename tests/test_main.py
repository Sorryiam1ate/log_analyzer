import os
import sys
import tempfile
from argparse import Namespace
from datetime import date, timedelta

import pytest

from main import main, run_report
from conftest import create_temp_log, create_temp_report


def test_basic_report_generation():
    log_line = (
        '{"@timestamp": "2024-07-22T10:20:00", '
        '"url": "/api/test", '
        '"response_time": 0.2}\n'
    )
    temp_log_path = create_temp_log(log_line)
    report_path = create_temp_report()
    args = Namespace(
        file=[temp_log_path],
        report=report_path,
        date=None
    )
    run_report(args)
    with open(report_path) as f:
        content = f.read()
        assert "/api/test" in content
        assert "0.20" in content
    os.remove(temp_log_path)
    os.remove(report_path)


def test_non_existent_file():
    args = Namespace(
        file=["None_existing_name.log"],
        report="Some_report.txt",
        date=None
    )
    with pytest.raises(FileNotFoundError):
        run_report(args)


def test_wrong_data():
    log_line = '123'
    with tempfile.NamedTemporaryFile(
        mode='w+',
        delete=False
    ) as temp_log:
        temp_log.write(log_line)
        temp_log_path = temp_log.name
    args = Namespace(
        file=[temp_log_path],
        report="Some_report.txt",
        date=None
    )
    with pytest.raises(RuntimeError):
        run_report(args)
    os.remove(temp_log_path)


def test_wrong_date_format(capsys):
    log_line = (
        '{"@timestamp": "13-07-2024T10:20:00", '
        '"url": "/api/test", '
        '"response_time": 0.2}\n'
    )
    with tempfile.NamedTemporaryFile(
        mode='w+',
        delete=False
    ) as temp_log:
        temp_log.write(log_line)
        temp_log_path = temp_log.name
    args = Namespace(
        file=[temp_log_path],
        report="Some_report.txt",
        date="2023-07-22"
    )
    run_report(args)
    captured = capsys.readouterr()
    assert "⚠️ Неверный формат даты" in captured.out
    os.remove(temp_log_path)


def test_average_value_accuracy():
    log_line = [
        (
            '{"@timestamp": "2024-07-22T10:20:00", '
            '"url": "/api/test", '
            '"response_time": 0.2}\n'
        ),
        (
            '{"@timestamp": "2024-07-22T10:20:00", '
            '"url": "/api/test", '
            '"response_time": 0.1}\n'
        ),
        (
            '{"@timestamp": "2024-07-22T10:20:00", '
            '"url": "/api/test", '
            '"response_time": 0.3}\n'
        ),
    ]
    temp_log_path = create_temp_log(log_line)
    report_path = create_temp_report()
    args = Namespace(
        file=[temp_log_path],
        report=report_path,
        date=None
    )
    run_report(args)
    with open(report_path) as f:
        content = f.read()
        assert "0.20" in content
    os.remove(temp_log_path)
    os.remove(report_path)


def test_main_args(monkeypatch):
    test_args = [
        "main.py",
        "--file",
        "log.json",
        "--report",
        "report.txt"
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    called = {}

    def fake_run_report(args):
        called["file"] = args.file
        called["report"] = args.report
        called["date"] = args.date
    monkeypatch.setattr(
        "main.run_report",
        fake_run_report
    )
    main()
    assert called["file"] == ["log.json"]
    assert called["report"] == "report.txt"
    assert called["date"] is None


def test_date_in_future():
    future_date = (
        date.today() + timedelta(days=5)
    ).strftime("%Y-%m-%d")
    args = Namespace(
        file=["test_log.json"],
        report="report.txt",
        date=future_date
    )
    with pytest.raises(
        ValueError,
        match="Неверный формат даты: используйте YYYY-MM-DD"
    ):
        run_report(args)
