import logging
from unittest.mock import patch

from expense_calculator import (
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

LIST_OF_ITEMS = [(987,"Chicken"),(456,"Bananas"),(789,"Pizza")]


@pytest.fixture
def runner():
   return CliRunner() 


def test_export_python_to_return_repr_string(runner: CliRunner):
    with patch("main.read_db_or_init", return_value=MOCK_OUTPUT_2_ITEMS):
        result = runner.invoke(export_python)
        printed_output = result.output.strip()
        assert printed_output == repr(MOCK_OUTPUT_2_ITEMS)
        assert result.exit_code == 0


def test_import_correct_csv_and_db_interaction(runner: CliRunner):
    with runner.isolated_filesystem():
        with open('test.csv', 'w') as file:
            file.write('amount,description\n50,Test 1\n75,Test 2\n')

        result = runner.invoke(import_csv, ['test.csv'])
        assert result.exit_code == 0  
        assert 'Pomyślnie zaimportowano' in result.output


def test_report_function_and_output_verification(runner: CliRunner):
    with patch("main.read_db_or_init", return_value=MOCK_OUTPUT_2_ITEMS):
        result = runner.invoke(report)
        printed_output = result.output
        assert "==ID==  ==Amount==  =BIG?=  =DESCRIPTION=" in printed_output
        assert "1" and "34" and "Hit Box" in printed_output
        assert "2" and "453" and "Crazy curry" in printed_output
        assert "TOTAL:" and "487" in printed_output
        assert result.exit_code == 0


def test_add(runner: CliRunner):
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