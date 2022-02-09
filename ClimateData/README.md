Readme File

database.py info:
You will need to install psycopg2 to interact with the database. The command that worked for me was "pip3 install psycopg2-binary".
There is a password variable near the top of the database.py file, make sure you enter your postgres password there if it is different.

When using the get data method, the tablename, columns(list) and ids(list) must be passed as strings. 
The id is the id without the years included, and can include or not include the leading zeros.
The start and end years must be passed in as integers. 
You will recieve an error message if you accidentally mispell the tablename or columns. 

If there are updates to processed files, you will need to first re-run preprocess.py, then drop the old tables and re-run setup database. 
There is a drop all tables function that you can call before calling the setup function again. 
There is also a drop table function if you need to drop a single table where you can just pass in the name of the table.
