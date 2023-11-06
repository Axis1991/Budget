"""Unittest module to test a few basic functionalities"""
from io import StringIO
import sys
import unittest
from unittest.mock import patch, mock_open

from main import (
    add_expense,
    create_Expense_item_from_dict,
    find_next_id,
    print_expenses,
    read_db_or_init,
    read_expenses,
    strip_zeros,
    CSV_import,
    Expense,
    
)

    # def setUp(self) -> None:
    #     return super().setUp()

    # def tearDown(self) -> None:
    #     return super().tearDown()


class TestExpenseClass(unittest.TestCase):
    """Verifies if invalid data is handled correctly by the class"""
    def test_negative_amount(self):
        with self.assertRaises(ValueError) as message:
            expense = Expense(id=1, amount=-1, description="Negative Expense")
            expense.__post_init__()

        self.assertEqual(str(message.exception), "Koszt nie może być ujemny")

    def test_empty_string(self):
        with self.assertRaises(ValueError) as message:
            expense = Expense(id=1, amount=1, description="")
            expense.__post_init__()
        self.assertEqual(str(message.exception), "Opis nie może być pusty")


class TestCsvImportClass(unittest.TestCase):
    """Verifies if data is handled correctly by CsvImport class """
    def test_correct_input(self):
        instance = CSV_import(amount="100.50", description="Valid Expense")
        self.assertIsInstance(instance, CSV_import)
        
    def test_negative_amount(self):
        with self.assertRaises(ValueError) as message:
            expense = CSV_import(amount="-1", description="Negative Expense")
            expense.__post_init__()

        self.assertEqual(str(message.exception), "Koszt nie może być ujemny")

    def test_wrong_format_value(self):
        with self.assertRaises(ValueError) as message:
            expense = CSV_import(amount="Pax", description="Amount NaN")
            expense.__post_init__()

        self.assertEqual(str(message.exception), "Wszystkie koszty muszą być liczbami")

    def test_empty_string(self):
        with self.assertRaises(ValueError) as message:
            expense = CSV_import(amount="1", description="")
            expense.__post_init__()
        self.assertEqual(str(message.exception), "Opis nie może być pusty")


class TestFindID(unittest.TestCase):
    """ Verifies if id is correctly selected in a number of situations"""
    def test_find_next_id_empty(self):
        empty = []
        self.assertEqual(find_next_id(empty), 1)

    def test_find_next_easy_path(self):
        someobject = [
            Expense(id=1, amount=234, description="Zabawki"),
            Expense(id=2, amount=334, description="Fish"),
        ]
        self.assertEqual(find_next_id(someobject), 3)

    def test_find_next_id_missing_number(self):
        someobject = [
            Expense(id=1, amount=234, description="Zabawki"),
            Expense(id=3, amount=76.23, description="Yt premium"),
        ]
        self.assertEqual(find_next_id(someobject), 2)


class TestReadDB(unittest.TestCase):
    """Tests the expected return value for database - existing or not"""
    @patch("pickle.load")
    @patch("builtins.open", new_callable=mock_open)
    def test_read_db_or_init_with_db(self, mock_file, mock_load):
        mock_expenses = [Expense(id=1, amount=234.0, description="Zabawki")]
        mock_load.return_value = mock_expenses
        got = read_db_or_init()
        self.assertEqual(got, mock_expenses)

    @patch("pickle.load")
    def test_read_db_or_init_no_db(self, mock_file):
        mock_file.side_effect = FileNotFoundError
        got = read_db_or_init()
        self.assertEqual(got, [])


class TestAddExpense(unittest.TestCase):
    """Tests if expenses are correctly added the list for single and multiple items"""
    def test_add_expense_single(self):
        expense_list = []
        add_expense(expense_list, amount=60, description="Pendrive")
        self.assertEqual(len(expense_list), 1)
        added_expense = expense_list[0]
        self.assertEqual(added_expense.amount, 60)
        self.assertEqual(added_expense.description, "Pendrive")
        self.assertEqual(added_expense.id, 1)

    def test_add_expense_multiple(self):
        expense_list = [(Expense(2, 22, "Dwójka"))]
        add_expense(expense_list, amount=60, description="Pendrive")
        add_expense(expense_list, amount=40, description="USB Cable")
        self.assertEqual(len(expense_list), 3),
        expense3 = expense_list[2]
        self.assertEqual(expense3.amount, 40)
        self.assertEqual(expense3.description, "USB Cable")
        self.assertEqual(expense3.id, 3)


class TestCreateExpenseItemFromDict(unittest.TestCase):
    """ Verifies if items are correctly interpreted from a dictionary and if 
    incorrect ones are handled correctly"""
    def test_valid_input(self):
        row = {"amount": "60", "description": "Pendrive"}
        expense = create_Expense_item_from_dict(row)

        self.assertIsInstance(expense, CSV_import)
        self.assertEqual(expense.amount, "60")
        self.assertEqual(expense.description, "Pendrive")

    def test_missing_amount_key(self):
        row = {"description": "Pendrive"}

        with self.assertRaises(SystemExit) as message:
            create_Expense_item_from_dict(row)

        self.assertEqual(message.exception.code, 1)

    def test_missing_description_key(self):
        row = {"amount": "60"}

        with self.assertRaises(SystemExit) as message:
            create_Expense_item_from_dict(row)

        self.assertEqual(message.exception.code, 1)

    def test_invalid_amount(self):
        row = {"amount": "abc", "description": "Invalid Amount"}

        with self.assertRaises(ValueError) as message:
            create_Expense_item_from_dict(row)

        self.assertEqual(str(message.exception), "Wszystkie koszty muszą być liczbami")


class TestReadExpenses(unittest.TestCase):
    """ Tests reading data from db for easy path and invalid entries"""
    @patch("main.create_Expense_item_from_dict", side_effect=create_Expense_item_from_dict)
    @patch("main.find_next_id", side_effect=find_next_id)
    @patch("builtins.open", create=True)
    def test_valid_input(self, mock_open, mock_create_expense, mock_find_id):
        mock_open.return_value.__enter__.return_value = StringIO(
            "amount,description\n60,Pendrive\n40,USB Cable"
        )

        expense_list = []

        expenses = read_expenses("temp_expenses.csv", expense_list)

        self.assertIsInstance(expenses, list)
        self.assertEqual(len(expenses), 2)
        self.assertIsInstance(expenses[0], Expense)
        self.assertEqual(expenses[0].amount, 60)
        self.assertEqual(expenses[0].description, "Pendrive")

    @patch("main.create_Expense_item_from_dict", side_effect=create_Expense_item_from_dict)
    @patch("main.find_next_id", side_effect=find_next_id)
    @patch("builtins.open", create=True)
    def test_invalid_input(self, mock_open, mock_create_expense, mock_find_id):
        mock_open.return_value.__enter__.return_value = StringIO(
            "amount,description\nWrong data"
        )

        expense_list = []

        try:
            with self.assertRaises(ValueError) as message:
                expenses = read_expenses("temp_expenses.csv", expense_list)
        except SystemExit as context:
            self.assertEqual(context.code, 1)


class TestStripZeroes(unittest.TestCase):
    """ Tests the correct removal of trailing zeroes"""
    def test_number_following_zeroes(self):
        got = strip_zeros(34.00)
        expected = "34"
        self.assertEqual(got, expected)

    def test_number_no_following_zeroes(self):
        got = strip_zeros(34)
        expected = "34"
        self.assertEqual(got, expected)


class TestPrintExpenses(unittest.TestCase):
    """ Tests the correct presentation of results to the user"""
    def test_print_expenses(self):
        expense_list = [Expense(1, 123.00, "Cherry"), Expense(2, 1000, "Garden swing")]

        captured_output = StringIO()
        sys.stdout = captured_output

        print_expenses(expense_list)
        output = captured_output.getvalue()

        sys.stdout = sys.__stdout__

        self.assertIn("==ID==  ==Amount==  =BIG?=  =DESCRIPTION=", output)
        self.assertIn("  2       1000        (!)    Garden swing", output)
        self.assertIn("  1       123                Cherry", output)
        self.assertIn("TOTAL:    1123", output)


if __name__ == "__main__":
    unittest.main()
