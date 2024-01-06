# Shazam Charts
Python files to extract shazam chart data (using RapidAPI) into SQLite3 to develop Power BI Reports.

## Before running the scripts
- Edit the directory path in each script to connect to the database.
  ```python
  db_path = os.path.join("Enter directory path here")
  ```
  For example:
  ```python
  db_path = os.path.join("C:\\", "Programs", "SQLite")
- Ensure that a database is created in SQLite for the connection.

## Shazam Charts Data Extraction Guide

1.	In the Windows Start Menu, open Windows Task Scheduler.
2.	Go to Action and select Create Task.
- Under the General tab, give the task a name and description. Under security options, select the user account and select the run option.
- Under the Triggers tab, select New and select the settings to trigger the task.
- Under the Actions tab, select New and select Browse to locate the program or script that needs to be scheduled.
- Under the Conditions tab, select any additional conditions required to trigger the task.
- Under the Settings tab, select any additional settings to trigger the task.
- Click OK.
3.	Repeat Step 2 to schedule another task.
4.	Go to File and click Exit or close Windows Task Sheduler when all tasks have been scheduled.

## Author
Shirley Li (06/01/2023)
