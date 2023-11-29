# Budget Test Smoke Suite.

Test Suite consists of unit and functional tests.
Unit tests are located in <code>test_exp_calc_unittest.py</code> file.
They cover individual functions used by Click commands.
Click commands functional tests are located in <code>test_exp_calc_pytest.py</code> and integration tests in <code>test_integration_exp_calc.py</code>.

### Unit tests
---

#### Expense class
Check if validation of Expense class is working as expected:
- number cannot be smaller than 0
- big numbers should be handled gracefully - <br>
  expected amount should not exceed 10bn
- if you type in something different than number, algorithm should handle the input gracefully

Expected result: 
- Validation works properly for values higher than 0 but low than 10bn
- ValueErrors are raised for negative, too high or wrong format data as well as empty string as description

#### Read_db_or_init
Check if reading database is working as expected, then introduce an error to a file.

Expected result:
- at first, data should be loaded correctly
- after introduction the error, data should not be loaded, user should get an error about not being able to retrieve errors from database
  

### Functional tests
---

#### **TC-01**
Check if click command <code> export_python</code> correcty displays python repr to be reused in the future is working as expected:
- test uses mock content to imitate returning content from database (function tested separately)

Expected result: 
- command is successfully executed with code 0
- content is read correctly from mocked database


#### **TC-02**
Check if click command <code>import_csv</code> correcty imports csv files:
- test uses temporary file and mock data
- patch is used to imitate connection to database

Expected result:
- click module runs successfully using CliRunner 
- database is called once when content from csv file is saved to it
- success message is displayed correctly


#### **TC-03**
Check if click command <code>report</code> correcty imports csv files:
- test used mock data
- patch is used to imitate connection to database

Expected result:
- click module runs successfully using CliRunner 
- with variable length of input, test checks relevant elements of the output

<br>
