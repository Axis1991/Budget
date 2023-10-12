import pytest
import click
import csv
from click.testing import CliRunner
from main import clack
from main import Expense, read_db_or_init, export_python, import_csv, DB_FILENAME
import pickle
from unittest.mock import mock_open, patch
import sys
import tempfile
import os


@pytest.fixture
def mock_expense_list():
    return


def test_export_python_working_capture(capsys):
    mock_output = [
        Expense(id=1, amount=34.0, description="Hit Box"),
        Expense(id=2, amount=453.0, description="Crazy curry"),
    ]

    with patch('main.read_db_or_init', return_value = mock_output):
        export_python()
        captured = capsys.readouterr()
        with pytest.raises(SystemExit):
            assert captured.out == repr(mock_output)


def test_export_python(capsys):
    runner = CliRunner()
    mock_output = [
        Expense(id=1, amount=34.0, description="Hit Box"),
        Expense(id=2, amount=453.0, description="Crazy curry"),
    ]

    with patch("main.read_db_or_init", return_value=mock_output):
        result = runner.invoke(export_python)
        captured = capsys.readouterr()

        assert captured.out.strip() == repr(mock_output)

    assert result.exit_code == 0



def test_import_csv(capsys):
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".csv") as temp_csv:
        temp_csv.write("34,Hit Box\n453,Crazy curry\n")

    mock_output = [
        Expense(id=1, amount=34.0, description="Hit Box"),
        Expense(id=2, amount=453.0, description="Crazy curry"),
    ]

    with patch("main.add_csv_to_db", return_value=mock_output), patch('main.save_db') as mock_save_db:
        import_csv(temp_csv.name)
        mock_save_db.assert_called_once_with(mock_output)
        captured = capsys.readouterr()
        assert captured.out.strip() == "Pomyślnie zaimportowano"
    
    os.remove(temp_csv.name)
