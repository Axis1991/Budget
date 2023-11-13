""" Pytest document testing a few basic functionalities"""

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

LIST_OF_ITEMS = [(987, "Chicken"),(456, "Bananas"),(789, "Pizza")]

@pytest.fixture
def runner():
   return CliRunner() 


@pytest.fixture
def temp_db_file(tmp_path):
    temp_file = tmp_path / "temp.json"
    return temp_file

@pytest.fixture
def setup_temp_db(temp_db_file):
    expense_list = []
    save_db(expense_list, filename=temp_db_file, overwrite=True)
    return expense_list

@pytest.fixture
def teardown_temp_db(temp_db_file):
    if temp_db_file.exists():
        temp_db_file.unlink()



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

    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".csv") as temp_csv:
        temp_csv.write("amount,description\n34,Hit Box\n453,Crazy curry\n")

    with patch("main.add_csv_to_db", return_value=MOCK_OUTPUT_2_ITEMS), patch(
        "main.save_db"
    ) as mock_save_db:
        result = runner.invoke(import_csv, [temp_csv.name])
        mock_save_db.assert_called_once_with(MOCK_OUTPUT_2_ITEMS)
        printed_output = result.output.strip()
        assert printed_output == "Pomyślnie zaimportowano"
    os.remove(temp_csv.name)


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

def test_add_and_report(runner, setup_temp_db, teardown_temp_db):
    temp_db_file = setup_temp_db
    try:
        global DB_FILENAME
        DB_FILENAME = temp_db_file
        for amount, description in LIST_OF_ITEMS:
            arguments = [str(amount), description]
            result = runner.invoke(add, arguments)
        assert result.output == "Dodano\n"

        # with open(DB_FILENAME, 'r') as file:
        #     file_contents = file.read()
        #     assert "1" and "2" and "3" in file_contents
        #     assert "987" and "456" and "789" in file_contents
        #     assert "Chicken" and "Bananas" and "Pizza" in file_contents

        cli_report = runner.invoke(report)
        printed_output = cli_report.output
        assert "1" and "2" and "3" in printed_output
        assert "987" and "456" and "789" in printed_output
        assert "Chicken" and "Bananas" and "Pizza" in printed_output

    finally:
        teardown_temp_db
        DB_FILENAME = "budget.json"