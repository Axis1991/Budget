""" Pytest document testing a few basic functionalities"""

import json
import logging
import os
import tempfile
import time
from unittest.mock import patch

from main import (
    Expense,
    add,
    add_csv_to_db,
    add_expense,
    clack,
    export_python,
    find_next_id,
    import_csv,
    print_expenses,
    read_db_or_init,
    read_expenses,
    report,
    save_db,
    DB_FILENAME
)

from click.testing import CliRunner
import pytest

MOCK_OUTPUT_2_ITEMS = [
        Expense(id=1, amount=34.0, description="Hit Box"),
        Expense(id=2, amount=453.0, description="Crazy curry"),
    ]

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

# @pytest.fixture
# def teardown_temp_db():
#     yield
#     os.remove("test_db.json")



def test_export_python(runner):
    """ Test for returning correct repr string"""
    with patch("main.read_db_or_init", return_value=MOCK_OUTPUT_2_ITEMS):
        result = runner.invoke(export_python)
        printed_output = result.output.strip()
        assert printed_output == repr(MOCK_OUTPUT_2_ITEMS)
        assert result.exit_code == 0


def test_import_csv(runner):
    """ Test to check if csv file is imported correctly and
     if there is appropriate interaction with database"""
    with runner.isolated_filesystem():
        with open('test.csv', 'w') as file:
            file.write('amount,description\n50,Test 1\n75,Test 2\n')

        result = runner.invoke(import_csv, ['test.csv'])
        assert result.exit_code == 0  
        assert 'Pomyślnie zaimportowano' in result.output


def test_report(runner):
    """ Test to check if click module runs correctly
      correctly and function output is printed as expected"""
    with patch("main.read_db_or_init", return_value=MOCK_OUTPUT_2_ITEMS):
        result = runner.invoke(report)
        printed_output = result.output
        assert "==ID==  ==Amount==  =BIG?=  =DESCRIPTION=" in printed_output
        assert "1" and "34" and "Hit Box" in printed_output
        assert "2" and "453" and "Crazy curry" in printed_output
        assert "TOTAL:" and "487" in printed_output
        assert result.exit_code == 0


def test_add(runner):
    """ Test verifying that add function correctly adds element to a class
      and then to the list of items in the database"""

    expense_list = []

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    with patch("main.read_db_or_init", return_value=expense_list), patch(
        "main.save_db") as mock_save_db:
        for amount, description in LIST_OF_ITEMS:
            arguments = [str(amount), description]
            result = runner.invoke(add, arguments)
        logger.info(f"Exit code: {result.exit_code}") # Po co to jest?
        assert result.output == "Dodano\n"
        assert Expense(id=1,amount=987,description="Chicken") in expense_list
        assert mock_save_db.call_count == 3
        mock_save_db.assert_called_with(expense_list, filename="budget.json")


################################################################################
                          # Integration tests
################################################################################

def test_add_and_report(runner, use_temp_db):
    temp_db = use_temp_db
    for amount, description in LIST_OF_ITEMS:
        result = runner.invoke(add, [str(amount), description, f"--filename={temp_db}"])
    assert result.output == "Dodano\n"

    cli_report = runner.invoke(report, ["--filename", temp_db])
    printed_output = cli_report.output
    assert "1" and "2" and "3" in printed_output
    assert "987" and "456" and "789" in printed_output
    assert "Chicken" and "Bananas" and "Pizza" in printed_output


def test_add_import_csv_and_report(runner, use_temp_db, use_temp_csv):
    temp_db = use_temp_db
    temp_csv = use_temp_csv
    for amount, description in LIST_OF_ITEMS:
        result = runner.invoke(add, [str(amount), description, f"--filename={temp_db}"])
    assert result.output == "Dodano\n"

    runner.invoke(import_csv, [temp_csv, f"--filename={temp_db}"])
    with open(temp_db, "r") as stream:
        db_content = json.load(stream)
        print(f"{db_content}")
        assert {'amount': "150.0", 'description': 'Test CSV 1', 'id': 4} in db_content
        assert {'amount': "300.0", 'description': 'Test CSV 2', 'id': 5} in db_content    

    cli_report = runner.invoke(report, ["--filename", temp_db])
    printed_output = cli_report.output
    print(f"{printed_output}")
    assert "1" and "2" and "3" in printed_output
    assert "987" and "456" and "789" in printed_output
    assert "Chicken" and "Bananas" and "Pizza" in printed_output
    assert "Chicken" and "Bananas" and "Pizza" in printed_output
    assert "4" and "Test CSV 1" and "150" in printed_output

    


