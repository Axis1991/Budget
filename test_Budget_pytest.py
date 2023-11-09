""" Pytest document testing a few basic functionalities"""

import os
import tempfile
from unittest.mock import patch

from main import (
    Expense,
    add,
    export_python,
    import_csv,
    report,
)

from click.testing import CliRunner
import pytest

MOCK_OUTPUT_2_ITEMS = [
        Expense(id=1, amount=34.0, description="Hit Box"),
        Expense(id=2, amount=453.0, description="Crazy curry"),
    ]

# read_db_or_init, find_next_id, add_csv_to_db, print_expenses, add_expense, save_db, - potentially to be tested

@pytest.fixture
def runner():
   return CliRunner() 

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
    test_amount = 123
    test_description = "Chicken"
    expense_list = []
    with patch("main.read_db_or_init", return_value=expense_list), patch(
        "main.save_db") as mock_save_db:
        result = runner.invoke(add, [str(test_amount), test_description])
        print(result.exit_code)
        assert result.output == "Dodano\n"
        assert Expense(id=1,amount=123,description="Chicken") in expense_list
        mock_save_db.assert_called_once_with(expense_list)
