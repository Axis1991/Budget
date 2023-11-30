""" Pytest document with integration tests using test database and CliRunner"""

import json
import os
from typing import Literal

from expense_calculator import (
    Expense,
    add,
    export_python,
    import_csv,
    report,
)

from click.testing import CliRunner
import pytest


LIST_OF_ITEMS = [(987,"Chicken"),(456,"Bananas"),(789,"Pizza")]


@pytest.fixture
def runner():
   return CliRunner() 

@pytest.fixture
def use_temp_csv():
    filename_csv = "temp.csv"
    with open(filename_csv, "w") as file:
        file.write('amount,description\n150,Test CSV 1\n300,Test CSV 2\n')  
    yield filename_csv
    os.remove(filename_csv)


@pytest.fixture
def use_temp_db():
    filename_db = "test_db.json"
    with open(filename_db, "w") as file:
        file.write("[]")  
    yield filename_db
    os.remove(filename_db)


def test_import_csv_and_export_python(runner: CliRunner, use_temp_db: Literal['test_db.json'], use_temp_csv: Literal['temp.csv']):
    temp_csv = use_temp_csv
    temp_db = use_temp_db
    runner.invoke(import_csv, [temp_csv, f"--filename={temp_db}"])
    result = runner.invoke(export_python, f"--filename={temp_db}")
    printed_output = result.output.strip()
    assert printed_output == repr([Expense(id=1, amount=150.0, description='Test CSV 1'), Expense(id=2, amount=300.0, description='Test CSV 2')])


def test_add_and_report(runner: CliRunner, use_temp_db: Literal['test_db.json']):
    temp_db = use_temp_db
    for amount, description in LIST_OF_ITEMS:
        result = runner.invoke(add, [str(amount), description, f"--filename={temp_db}"])
    assert result.output == "Dodano\n"

    cli_report = runner.invoke(report, ["--filename", temp_db])
    printed_output = cli_report.output
    assert "1" and "2" and "3" in printed_output
    assert "987" and "456" and "789" in printed_output
    assert "Chicken" and "Bananas" and "Pizza" in printed_output


def test_add_import_csv_and_report(runner: CliRunner, use_temp_db: Literal['test_db.json'], use_temp_csv: Literal['temp.csv']):
    temp_db = use_temp_db
    temp_csv = use_temp_csv
    for amount, description in LIST_OF_ITEMS:
        result = runner.invoke(add, [str(amount), description, f"--filename={temp_db}"])
    assert result.output == "Dodano\n"

    runner.invoke(import_csv, [temp_csv, f"--filename={temp_db}"])
    with open(temp_db, "r") as stream:
        db_content = json.load(stream)
        assert {'id': 4, 'amount': 150, 'description': 'Test CSV 1'} in db_content
        assert {'id': 5, 'amount': 300, 'description': 'Test CSV 2'} in db_content    

    cli_report = runner.invoke(report, ["--filename", temp_db])
    printed_output = cli_report.output
    print(f"{printed_output}")
    assert "1" and "2" and "3" in printed_output
    assert "987" and "456" and "789" in printed_output
    assert "Chicken" and "Bananas" and "Pizza" in printed_output
    assert "4" and "Test CSV 1" and "150" in printed_output