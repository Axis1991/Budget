import pytest
import click
import csv
from click.testing import CliRunner
from main import clack
from main import (
    Expense,
    read_db_or_init,
    find_next_id,
    export_python,
    add_csv_to_db,
    report,
    print_expenses,
    import_csv,
    add_expense,
    add,
    save_db,
    DB_FILENAME,
)
import pickle
from unittest.mock import mock_open, patch
import sys
import tempfile
import os
from io import StringIO


@pytest.fixture
def mock_expense_list():
    return


def test_export_python():
    runner = CliRunner()
    mock_output = [
        Expense(id=1, amount=34.0, description="Hit Box"),
        Expense(id=2, amount=453.0, description="Crazy curry"),
    ]
    with patch("main.read_db_or_init", return_value=mock_output):
        result = runner.invoke(export_python)
        printed_output = result.output.strip()
        assert printed_output == repr(mock_output)
        assert result.exit_code == 0


def test_import_csv():
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".csv") as temp_csv:
        temp_csv.write("amount,description\n34,Hit Box\n453,Crazy curry\n")

    mock_output = [
        Expense(id=1, amount=34.0, description="Hit Box"),
        Expense(id=2, amount=453.0, description="Crazy curry"),
    ]

    with patch("main.add_csv_to_db", return_value=mock_output), patch(
        "main.save_db"
    ) as mock_save_db:
        result = runner.invoke(import_csv, [temp_csv.name])
        mock_save_db.assert_called_once_with(mock_output)
        printed_output = result.output.strip()
        assert printed_output == "Pomyślnie zaimportowano"
    os.remove(temp_csv.name)


def test_report():
    runner = CliRunner()
    mock_output = [
        Expense(id=1, amount=34.0, description="Hit Box"),
        Expense(id=2, amount=453.0, description="Crazy curry"),
    ]
    with patch("main.read_db_or_init", return_value=mock_output):
        result = runner.invoke(report)
        printed_output = result.output
        
        assert "==ID==  ==Amount==  =BIG?=  =DESCRIPTION=" in printed_output
        assert "1" and "34" and "Hit Box" in printed_output
        assert "2" and "453" and "Crazy curry" in printed_output
        assert "TOTAL:" and "487" in printed_output
        assert result.exit_code == 0
        

# @pytest.mark.parametrize("amount, description, expected_result", [(123, "Chicken", "Dodano")])
def test_add():
    test_amount = 123
    test_description = "Chicken"
    expense_list = []
    runner = CliRunner()
    with patch("main.read_db_or_init", return_value=expense_list), patch(
        "main.save_db") as mock_save_db:
        result = runner.invoke(add, [str(test_amount), test_description])
        print(result.exit_code)
        assert result.output == "Dodano\n"
        assert Expense(id=1,amount=123,description="Chicken") in expense_list
        mock_save_db.assert_called_once_with(expense_list)

# new_callable - funkcja zmockowana

#edit for code review