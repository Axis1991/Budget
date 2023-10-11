"""
Usage: M07L12_projekt.py <add (amount, description)> <report> <import-csv(csv path)> <export-python>

Takes arguments to create or add to database budget.db and calculate the sum of expenses. Possible to load expenses from csv file.
<export-python> prints budget.db content in the form of a list to be possibly reused (hi there YAGNI ;) ).
"""

import csv
from dataclasses import dataclass
import pickle
import sys

import click

DB_FILENAME = "budget.db"


@dataclass
class Expense:
    id: int
    amount: float
    description: str

    def __post_init__(self):
        if float(self.amount) < 0:
            raise ValueError("Koszt nie może być ujemny")
        if not self.description:
            raise ValueError("Opis nie może być pusty")

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.amount == other.amount
            and self.description == other.description
        )

    def __post_repr__(self):
        return f"Expense(id={self.id!r}, description={self.description!r}, amount={self.amount!r})"


@dataclass
class CSV_import:
    amount: float
    description: str

    def __post_init__(self):
        if self.amount[0] == "-":
            raise ValueError("Koszt nie może być ujemny")
        if "." not in self.amount:
            if not self.amount.isnumeric():
                raise ValueError("Wszystkie koszty muszą być liczbami")
        else:
            counter = 0
            for each in self.amount:
                if each == ".":
                    counter += 1
                    if counter > 1:
                        raise ValueError("Wszystkie koszty muszą być liczbami")
                elif not each.isnumeric():
                    raise ValueError("Wszystkie koszty muszą być liczbami")

        if not self.description:
            raise ValueError("Opis nie może być pusty")


def find_next_id(expense_list: list[Expense]):
    ids = {item.id for item in expense_list}
    counter = 1
    while counter in ids:
        counter += 1
    return counter


def read_db_or_init() -> list[Expense]:
    try:
        with open(DB_FILENAME, "rb") as stream:
            expense_list = pickle.load(stream)
    except FileNotFoundError:
        expense_list = []
    return expense_list


def save_db(expense_list: list[Expense], overwrite: bool = True) -> None:
    mode = "wb" if overwrite else "xb"
    with open(DB_FILENAME, mode) as stream:
        pickle.dump(expense_list, stream)


def add_expense(expense_list: list[Expense], amount: float, description: str) -> None:
    expense_item = Expense(
        id=find_next_id(expense_list), amount=amount, description=description
    )
    expense_list.append(expense_item)


def create_Expense_item_from_dict(row: dict[str, str]) -> [CSV_import]:
    try:
        return CSV_import(description=row["description"], amount=(row["amount"]))
    except KeyError:
        print("Błąd pliku - akceptowalne pliki z kluczami 'amount' oraz 'description'")
        sys.exit(1)


def read_expenses(filename: str, expense_list) -> list[Expense]:
    with open(filename, encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        try:
            expenses_no_id = [create_Expense_item_from_dict(row) for row in reader]
            expenses_csv = [
                Expense(
                    find_next_id(expense_list),
                    float(expense.amount),
                    expense.description,
                )
                for expense in expenses_no_id
            ]
            return expenses_csv
        except ValueError as f:
            print(f"Błąd - {f.args[0]}")
            sys.exit(1)


def add_csv_to_db(csv_file):
    # Tested manually, csv content successfully added to db.
    # Exceptions correctly raised for incorrect data format or missing columns with appropriate messages.
    expense_list = read_db_or_init()
    expenses_csv = read_expenses(csv_file, expense_list)
    [expense_list.append(each) for each in expenses_csv]
    return expense_list


def strip_zeros(number: float) -> str:
    return str(number).rstrip("0").rstrip(".") if "." in str(number) else str(number)


def print_expenses(expense_list: list[Expense]) -> None:
    print(f"==ID==  ==Amount==  =BIG?=  =DESCRIPTION=")
    total = 0
    for item in expense_list:
        total += float(item.amount)
        if item.amount >= 1000:  # float?
            big = "(!)"
        else:
            big = " "
        print(
            f"{item.id:^6}    {strip_zeros(item.amount):<8}   {big:^6}  {item.description:<20}"
        )
    print("TOTAL:   ", f"{strip_zeros(total)}")


@click.group()
def clack():
    pass


@clack.command()
def export_python():
    expense_list = read_db_or_init()
    print(repr(expense_list))
#capsys - przeczytać dokumentację

@clack.command
@click.argument("csv_file")
def import_csv(csv_file):
    expense_list = add_csv_to_db(csv_file)
    save_db(expense_list)
    print("Pomyślnie zaimportowano")


@clack.command()
def report() -> None:
    expenses = read_db_or_init()
    print_expenses(expenses)


@clack.command()
@click.argument("amount")
@click.argument("description")
def add(amount: float, description: str) -> None:
    try:
        amount = float(amount.replace(",", "."))
    except ValueError:
        print("Błąd - Koszt musi być liczbą")
        sys.exit(1)
    expense_list = read_db_or_init()
    try:
        add_expense(expense_list, amount, description)
    except ValueError as e:
        print(f"Błąd - {e.args[0]}")
        sys.exit(1)
    save_db(expense_list)
    print("Dodano")


if __name__ == "__main__":
    clack()


# Napisz program, który ułatwi milionom Polaków śledzenie własnych wydatków oraz ich analizę. Program pozwala na łatwe dodawanie nowych wydatków i generowanie raportów. Aplikacja działa także pomiędzy uruchomieniami, przechowując wszystkie dane w pliku. Każdy wydatek ma id, opis oraz wielkość kwoty.

# 1. Program posiada podkomendy add, report, export-python oraz import-csv.

# 2. Podkomenda add pozwala na dodanie nowego wydatku. Należy wówczas podać jako kolejne argumenty wiersza poleceń wielkość wydatku (jako int) oraz jego opis (w cudzysłowach). Na przykład:
# $ python budget.py add 100 "stówa na zakupy".
# Jako id wybierz pierwszy wolny id - np. jeśli masz już wydatki z id = 1, 2, 4, 5, wówczas wybierz id = 3.

# 3. Podkomenda report wyświetla wszystkie wydatki w tabeli. W tabeli znajduje się także kolumna "big?", w której znajduje się ptaszek, gdy wydatek jest duży, tzn. co najmniej 1000. Dodatkowo, na samym końcu wyświetlona jest suma wszystkich wydatów.

# 4. Podkomenda export-python wyświetla listę wszystkich wydatków jako obiekt (hint: zaimplementuj poprawnie metodę __repr__ w klasie reprezentującej pojedynczy wydatek).

# 5. Podkomenda import-csv importuję listę wydatków z pliku CSV.

# 6. Program przechowuje pomiędzy uruchomieniami bazę wszystkich wydatków w pliku budget.db. Zapisuj i wczytuj stan używając modułu pickle. Jeżeli plik nie istnieje, to automatycznie stwórz nową, pustą bazę. Zauważ, że nie potrzebujemy podpolecenia init.

# 7. Wielkość wydatku musi być dodatnią liczbą. Gdzie umieścisz kod sprawdzający, czy jest to spełnione? W jaki sposób zgłosisz, że warunek nie jest spełniony?
