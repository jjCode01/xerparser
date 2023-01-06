# Change Log  
## 0.5.3 - 2023-01-05
### General Notes
* Small amount of refactoring and moving around files.
* Added gt and lt dunder methods to some of the classes.
* Using decorator to round any class method that returns a float. Just playing with decorators, may switch back to rounding directly in the method.
---
## 0.5.2 - 2023-01-02
### General Notes  
* Removed dependency on `Pydantic`. Speeds up code by ~25%.
### Added
* Added testing of `errors` attribute of `Xer` class.
### Changed
* Moved functions `is_workday`, `iter_holidays`, and `iter_workdays` to be methods of the `CALENDAR` class.
* The `budgeted_cost`, `actual_cost`, `this_period_cost`, and `remaining_cost` properties of the `TASK` class now return float values rounded to two decimal places. **Warning**: this may cause the `PROJECT` level values to be off by .01 from what was previously reported; you will need to recreate test data.  
### Removed
* Removed `has_predecessor`, `has_successor`, `has_finish_successor`, and `has_start_successor` of `TASK` class. These analyses can be done in the users program.
### In Development
* Continue working on Warnings class.
---
## 0.5.1 - 2022-12-31
### General Notes
* Updated tests.  
* More testing has resulted in minor code cleanup and refactoring.
### Changes
* The `description` attribute of `ACCOUNT` class will now return an empty string if its empty; it used to return None.
* Fixed bug in parser that was stripping out the last values (columns) in a table row if they were empty. This was causing validation errors with missing attributes in Pydantic.
* Changed `CALENDAR` class variable `CALENDAR_TYPES` (dict) to `CalendarTypes` (Enum).  
* `wbs` argument is now required during initialization of a `TASK` object.
* `predecessor` and `successor` arguments are now required during initialization of a `TASKPRED` object.
---  
## 0.5.0 - 2022-12-29
### General Notes
* This change focused on parsing Activity Code Data stored in a .xer file. This information is stored in the `ACTVTYPE`, `ACTVCODE`, and `TASKACTV` Tables.  
* **WARNING**: Some refactoring includes breaking changes, so this is being considered a `minor` version bump rather than a `patch`.
### Added
* Added `ACTVTYPE` class to represent Activity Code Types.
* Added `ACTVCODE` class to represent Activity Code Values.
* Added `activity_code_types` (dict), `activity_code_values` (dict), `wbs_nodes` (dict), `tasks` (dict) and `relationships` (dict) attributes to `Xer` class. 
* Added `activity_codes` attribute to `TASK` class, which holds a dict of `ACTVTYPE`, `ACTVCODE` pairs assigned to a task via the `TASKACTV` Table.
* Added `activity_codes` attribute to `PROJECT` class, which holds Project level activity code types.
* Added `relationships_by_hash` property to `PROJECT` class. Returns a dict with a hash of the relationship as the key and the relationship as the value. This is usefull for evaluating logic changes between two schedules; Unique IDs will change from schedule to schedule, but the hash value will be the same. Note: hash value is calculated based on predecessor task_code, successor task_code, and relationship link.
### Changed
* Moved `conv_excel_date` function from `dates.py` to a Static Method of the `CALENDAR` class. This function is only used to parse dates in the `clndr_data`.
* Moved `CALENDAR_TYPES` from being a Global variable in `calendars.py` to be a `CALENDAR` class variable.
* The Global Regular Expression variables in `calendars.py` now use the `re.compile` method.
* Renamed `fin_dates_id` attribute of `FINDATES` class to `uid`. This is consistent with the naming in other classes.
* Renamed `fin_dates_name` attribute of `FINDATES` class to `name`. This is consistent with the naming in other classes.
* `MEMOTYPE` and `TASKMEMO` classes no longer iherit from Pydantic BaseModel class. All attributes of both `MEMOTYPE` and `TASKMEMO` are strings, so type validation is not needed.
* Added `__eq__` and `__hash__` methods to `MEMOTYPE` class.
* Moved Enumerators `ConstraintType`, `PercentType`, `TaskStatus` and `TaskType` to inside the `TASK` class.
* Refactored how `calendars`, `wbs_nodes`, `tasks` and `relationships` attributes are assigned for the `PROJECT` class. Each of these attributes is now a list rather than a dict or set. These objects are now referenced directly in the `Xer` class as a dict using its Unique ID as the key, so the `PROJECT` reference to these objects can now be a simple list.
* `PROJECT` properties `actual_cost`, `budgeted_cost`, `remaining_cost`, and `this_period_cost` now return float values rounded to two decimal places.
### Removed
* Removed `__str__` method from `WeekDay` class in `calendars.py`. This was originally used for testing and is no longer needed.
* Removed `print_cal` method from `CALENDAR` class. This were originally used for testing and is no longer needed.
---  
## 0.4.1 - 2022-12-21
### General Note
This change focused on parsing Financial Periods and Past Period Data stored in a .xer file. This information is stored in the `FINDATES`, `TASKFIN` and `TRSRCFIN` Tables. 
### Added  
* Added `FINDATES` class to represent Financial Periods.
* Added `TASKFIN` class to represent Activity Past Period Actuals.
* Added `TRSRCFIN` class to represent Activity Resource Assignment Past Period Actuals.
* `Xer` class now has `financial_periods` (dict) attribute, which stores `FINDATES` objects.
* `TASK` class now has a `periods` (list) attribute, which stores `TASKFIN` objects.
* `TASKRSRC` class now has a `periods` (list) attribute, which stores `TRSRCFIN` objects.
### Changed
* `resources` attribute of `TASK` class changed from type list to type dict. This allows for easier assignment of financial period data (`TRSRCFIN`) to task resources (`TASKRSRC`).
---  
## 0.4.0 - 2022-12-20
### General
* General code clean up and refactoring
### Added  
* `Xer` class now has a class variable `CODEC`, which stores the type of encoding for a .xer file.
* Added `LinkToTask` class for use in storing a `TASK` objects predecessor and successor links. Has properties `task`, `link`, and `lag`.
* `TASK` objects now have a `predecessors` attribute, which holds a list of `LinkToTask` objects representing predecessor logic ties.
* `TASK` objects now have a `successors` attribute, which holds a list of `LinkToTask` objects representing successor logic ties.
* `TASK` objects now have a `has_predecessor` property, which return True if task has at least one predecessor stored in its `predecessors` attribute.
* `TASK` objects now have a `has_successors` property, which return True if task has at least one successor stored in its `successors` attribute.
* `TASK` objects now have a `has_finish_successor` property, which return True if task has at least one *Finish-Start* or *Finish-Finish* logic tie (link) stored in its `successors` attribute. Will also return True if the task has no successors.
* `TASK` objects now have a `has_start_predecessor` property, which return True if task has at least one *Finish-Start* or *Start-Start* logic tie (link) stored in its `predecessors` attribute. Will also return True if the task has no predecessors.
### Changed
* `Xer` class no longer accepts raw .xer files as an argument. The xer file must be decoded into a string, which is then passed as an argument. This helps avoid multiple try / except statements to read the xer file. 
* `xer_to_dict` function no longer returns a dictionary with a 'tables' key. Each table name is now a top level key in the dictionary.
* `xer_to_dict` function no longer parses the potential **errors** in the xer files. Errors are now parsed when the `Xer` object is initialized.
* `Xer` attribute `notebook` is renamed to `notebook_topic` to better define the objects stored in this attribute.
* `Xer` attribute `export` is renamed to `export_info` to better define the values stored in this attribute.
### In Development
* Working on a `ScheduleWarnings` class to provide schedule health analysis.
