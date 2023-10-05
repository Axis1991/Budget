from main import (
    find_next_id,
    read_db_or_init,
    save_db,
    add_expense,
    create_Expense_item_from_dict,
    read_expenses,
    strip_zeros,
    import_csv,
    Expense,
    CSV_import,
    DB_FILENAME,
)
from dataclasses import dataclass
import pickle, csv
import unittest
from unittest.mock import patch, mock_open
from io import StringIO
import sys


class TestExpenseClass(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()


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
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()
    
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
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

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
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()
    
    @patch("pickle.load")
    @patch("builtins.open", new_callable=mock_open)
    def test_read_db_or_init_with_db(self, mock_file, mock_load):
        # The mock data that we expect from the database
        mock_expenses = [
            Expense(id=1, amount=234.0, description="Zabawki")
        ]

        # Set the return value for the mock pickle.load function
        mock_load.return_value = mock_expenses

        # Call the actual function we want to test
        got = read_db_or_init()

        # Assert that our function returns the mocked data
        self.assertEqual(got, mock_expenses)


    @patch("pickle.load")
    def test_read_db_or_init_no_db(self, mock_file):
        mock_file.side_effect = FileNotFoundError
        got = read_db_or_init()
        self.assertEqual(got, [])
        

class TestReadDataBase(unittest.TestCase):

    def test_read_db_or_init_with_db(self):
        # The mock data that we expect from the database
        mock_expenses = [
            Expense(id=1, amount=234.0, description="Zabawki"),
            Expense(id=2, amount=334.0, description="Fish"),
            Expense(id=3, amount=76.23, description="Yt premium")
        ]

        # Serialize mock_expenses to simulate reading from a file.
        mock_data = pickle.dumps(mock_expenses)

        # Mocking open
        m = mock_open(read_data=mock_data)

        with patch('builtins.open', m):
            # Mocking pickle.load
            with patch('pickle.load') as mock_load:
                mock_load.return_value = mock_expenses
                
                # Call the actual function we want to test
                got = read_db_or_init()

                # Assert that our function returns the mocked data
                self.assertEqual(got, mock_expenses)

class TestAddExpense(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()
    
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
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

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

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    @patch('M07L12_projekt.create_Expense_item_from_dict', side_effect=create_Expense_item_from_dict)
    @patch('M07L12_projekt.find_next_id', side_effect=find_next_id)
    @patch('builtins.open', create=True)
    def test_valid_input(self, mock_open, mock_create_expense, mock_find_id):
        mock_open.return_value.__enter__.return_value = StringIO("amount,description\n60,Pendrive\n40,USB Cable")

        expense_list = []

        expenses = read_expenses("temp_expenses.csv", expense_list)

        self.assertIsInstance(expenses, list)
        self.assertEqual(len(expenses), 2)
        self.assertIsInstance(expenses[0], Expense)
        self.assertEqual(expenses[0].amount, 60)
        self.assertEqual(expenses[0].description, "Pendrive")


    @patch('M07L12_projekt.create_Expense_item_from_dict', side_effect=create_Expense_item_from_dict)
    @patch('M07L12_projekt.find_next_id', side_effect=find_next_id)
    @patch('builtins.open', create=True)
    def test_invalid_input(self, mock_open, mock_create_expense, mock_find_id):
        mock_open.return_value.__enter__.return_value = StringIO("amount,description\nWrong data")

        expense_list = []

        try:
            with self.assertRaises(ValueError) as message:
                expenses = read_expenses("temp_expenses.csv", expense_list)
        except SystemExit as context:
            self.assertEqual(context.code, 1)


if __name__ == "__main__":
    unittest.main()
