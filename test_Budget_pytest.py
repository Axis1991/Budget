import pytest
import click
import csv
from click.testing import CliRunner
from main import clack
from main import Expense, read_db_or_init, export_python, import_csv, DB_FILENAME
from unittest.mock import mock_open, patch
import sys

@pytest.fixture
def mock_expense_list():
    return 

def test_export_python():

    runner = CliRunner()
    result = runner.invoke(clack, ['export_python'])

    assert result.exit_code == 2



