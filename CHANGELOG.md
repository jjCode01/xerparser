
# Changelog - xerparser

## 0.13.1 - 2024-10-09

* `Node` object now use `seq_num` attribute for comparison and sorting.
* Fixed potential bug in how children are stored in the `Node` class; switched from a list to a dict to avoid having multiple of the same child.

---

## 0.13.0 - 2024-10-06  

NOTE: If you have tests setup, this change will require you to delete the existing `xer_data.json` fixture and recreate it in the test process.

* Added functionality for traversing `Node` objects:
    * `traverse_parents` method iterates through parents to root node.
    * `traverse_children` method iterates through all children to leaves.
    * `height` property is the length of the longest downward path to a leaf from a given node (leaf nodes with have a height of 0).
    * `depth` property is the length of the path to the root node from a given node (root node will have a depth of 0).  

---

## 0.12.3 - 2024-09-14

* Fixed potential KeyErrors in the `SCHEDOPTIONS` class due to missing attributes in files exported from older versions of P6. [Issue #7](https://github.com/jjCode01/xerparser/issues/7)
* Fixed bug where `create_date` and `update_date` attributes of the `TASK` class may be empty. [Issue #8](https://github.com/jjCode01/xerparser/issues/8)

---

## 0.12.2 - 2024-07-04

* Added `tasks` (list[`TASK`]) attribute to `PROJWBS` class.
* Added `task_rsrcs` (list[`TASKRSRC`]) attribute to `RSRC` class.

---

## 0.12.1 - 2024-07-02

Patched potential errors when transformming from a string to a float. Some languages use a comma rather than a period in floating point numbers.

---

## 0.12.0 - 2024-06-19

* Added class `RSRCRATE` which represents a Resource Rate. This can be accessed from the `resource_rate` (dict) attribute of the `Xer` object. [Issue #6](https://github.com/jjCode01/xerparser/issues/6)  

---  

## 0.11.2 - 2024-05-25

* Refactored inheritance for `Node` objects.
    * The `description` attribute of the `ACTVCODE` and `PCATVAL` classes has been changed to `name`.

---

## 0.11.1 - 2024-05-24

* Fixed bug in the equal override function for the `RSRC` object; missing a return.

---

## 0.11.0 - 2024-04-28

* Updated type hints, which now requires a minimum of Python 3.11.
* `RSRC` class now inherits from `Node`.
* Updating / filling in docstrings.

---

## 0.10.4 - 2024-03-08

* Updated dependencies to new versions.
* `ACCOUNT` class equal overide now checks if other object is None type.
* The `max_multiple_longest_path` attribute of the `SCHEDOPTIONS` class can be type int or None.

---

## 0.10.3 - 2023-08-11

### Changes

* Added `Node` class to represent a Tree data structure - can have one parent and multiple children. `ACCOUNT`, `ACTVCODE`, `PCATVAL`, and `PROJWBS` classes now inherit from `Node` class.

---

## 0.10.2 - 2023-08-05

### Changes

* Updated dependency `html-sanitizer` to the latest version `2.2.0`
* Added `Node` class to represent a Tree data structure - can have one parent and multiple children.
* `ACCOUNT`, `ACTVCODE`, `PCATVAL`, and `PROJWBS` classes now inherit from `Node` class.

---

## 0.10.1 - 2023-08-05

### Added

* Added `is_wbs` property to `TaskType` enum class. Checks if task is a wbs summary type.

---

## 0.10.0 - 2023-07-17

### Added

* Added `wbs_root` attribute to the `PROJECT` class. This is the root WBS node.
* Added `children` attribute to the `PROJWBS` class. Along with the `wbs_root` above, this forms a Tree Data Structure.
* Added `children` attribute to the `ACCOUNT` class.
* Added `children` attribute to the `ACTVCODE` class.
* Added `children` attribute to the `PCATVAL` class.

### Changes

* Changed the `PROJECT` `name` from an attribute to a property. The project name is stored in the `wbs_root` added above.

---

## 0.9.9 - 2023-06-14

### Changes

* The `task_percent` property of the `PROJECT` class now ignores Level of Effort activities when calculating percent complete. There were edge cases where the LOE activity had a remaining duration much greater than its original duration, which significantly reduced the calculated percent complete.

---

## 0.9.8 - 2023-05-24

* Bug fixes with validating data types for `TASKPRED` objects.

---

## 0.9.7 - 2023-05-24

* Bug fixes with validating data types for `TASK` objects.

---

## 0.9.6 - 2023-05-14

### Added

* Added `resources` attribute containing a list of `TASKRSRC` objects to the `PROJECT` class. Previously, `TASKRSRC` objects were only accessible through a `TASK` object. 

---

## 0.9.5 - 2023-05-13

### General

Both project specific and global calendars are now included in the `PROJECT` `calendars` attribute. Covers cases where project tasks are assigned to a gobal calendar.

---

## 0.9.4 - 2023-04-19

### Added

* Added `actual_duartion` property to `PROJECT` class.

---

## 0.9.3 - 2023-04-08

### General

Some code cleanup and corrections to the python code in the README file.

---

## 0.9.2 - 2023-03-19

### Added

* Added function `file_reader` which accepts a .xer file and reads it to a string object.
    * Accepts str or Path objects for files stored locally or on a server.
    * Accepts BinaryIO files from requests, Flask, FastAPI, etc...
* Added classmethods `reader` to the `Xer` class. A .xer file can be passed directly to this method, which will read and decode the file, and return a `Xer` object. Uses the `file_reader` function above.

### Changed

* Changed name of function `xer_to_dict` to `parser`.

---

## 0.9.1 - 2023-03-18

Updated `CorruptXerFile` Exception to receive the list of errors and print them out when the exception is raised. The errors can now be accessed from the Exception when using `try` `except`.

```python
try:
    xer = Xer(file_contents)
except CorruptXerFile as e:
    for error in e.errors:
        print(error)
```

---

## 0.9.0 - 2023-03-17

### General Notes

Remove `error` attribute from `xer` class. If the errors are encoutered during initialization of an `xer` object, then a `CorruptXerFile` Exception is raised.

### Added

* `find_xer_errors` function. Error checking for the file is now its own function that that can find errors in an xer file and povide the results in a list.
* Error checking now looks for invalid `rsrc_id` assigned to a `TASKRSRC` object.

### Removed

The option for None type on the following items was originally done to avoid Exceptions being thrown if the file is corrupted. This created additional code to handle situations when the attributes equal None.
* Removed option for `calendar` attribute of the `TASK` class to be type `None`; All `TASK` objects must have a `calendar` or the `CorruptXerFile` Exception is raised. 
* Removed option for the `resource` attribute of the `TASKRSRC` class to be type `None`; all `TASKRSRC` objects must have a `resource` or the `CorruptXerFile` Exception is raised.

---

## 0.8.2 - 2023-03-05

### Added

* Added `actual_total_cost` property to `TASKFIN` class
* Added `late_start` property to `PROJECT` class

### Changes

* `TASK` method `rem_hours_per_day` can now accept a `late` flag (bool) to calculate late dates rather than early dates.

---

## 0.8.1 - 2023-02-28

### General Notes

Refactor / cleanup code.
Working on functionality to generate cost loading projections.

### Added

* Added `rem_hours_per_day` method to `TASK` class. This return a dict with date: workhour key value pairs. This function was originally contained within the `calendar.py` module, but was not being used. Makes more sense to have it as a `TASK` method.
* Added `base_calendar` attribute to `CALENDAR` class. The `is_workday` function will now search the `base_calendar` for holidays when determining if a date is a workday.

### Changed

* `remain_drtn_hr_cnt` attribute of `TASK` no longer allows `None` type.
* `finish` property of `TASK` will now check for `reend_date` and return it before it returns `early_end_date`

---

## 0.8.0 - 2023-02-28

### General Notes

Added parsing of User Defined Fields (UDF). [Issue #4](https://github.com/jjCode01/xerparser/issues/4)  
Expanded testing for more coverage.  
Refactor / clean up code for initialization of `XER` class.

### Added

* Added class `UDFTYPE` which represents a User Defined Field.
* Added attribute `user_defined_fields` to `PROJECT`, `PROJWBS`, `RSRC`, and `TASK` classes, which hold a dictionary of `UDFTYPE`: `UDF Value` key value pairs.

---

## 0.7.0 - 2023-02-25

### General Notes

Added parsing of Project Codes. [Issue #3](https://github.com/jjCode01/xerparser/issues/3).

### Added

* Added class `PCATTYPE` which represents a Project Code Type.
* Added class `PCATVAL` which represents a Project Code Value.
* Added attribute `project_code_types` to `Xer` class, which holds a dictionary of `PCATTYPE` objects.
* Added attribute `project_code_values` to `Xer` class, which holds a dictionary of `PCATVAL` objects.
* Added attribute `project_codes` to `PROJECT` class, which holds a dictionary of `PCATTYPE`: `PCATVAL` key value pairs assigned to a project.

---

## 0.6.0 - 2023-02-24

### General Notes

The `ScheduleWarnings` class will no longer be developed under this project. This is a breaking change if you were using the `ScheduleWarnings` class.

### Added

* Added `__len__` method to `CALENDAR` class. Returns number of workdays in a week.

### Removed

* Removed `warnings.py` from project. This may become a seperate project.

---

## 0.5.9 - 2023-02-12

* Added `default_calendar` attribute to `PROJECT` class.

---

## 0.5.8 - 2023-02-05

### Added

* Added `SCHEDOPTIONS` class.
* Added `options` attribute the `PROJECT` class, which is a `SCHEDOPTIONS` object.`
* Added `lineage` and `full_code` properties to the `ACTVCODE` class. [Issue #2](https://github.com/jjCode01/xerparser/issues/2)

### Changes

* Comparison operators for `ACTVCODE` are now based on `full_code` property rather than `code` property.

---

## 0.5.7 - 2023-02-03

### General Notes

Added some additional features noted below, and continue working on `Warnings` class.

### Added

* Added `lineage` property to `PROJWBS` class. Returns list of all ancestor `PROJWBS` objects, including self.
* Added `duration` property to `TASK` class. This will return `remaining_duration` if the task is not started; otherwise, it returns `original_duration`. This is usefull when the remaining duration is unlinked from the original duration in the project settings - in these cases, the remaining duration can be different to the original duration in tasks that have not started.

---

## 0.5.6 - 2023-01-24

Fixed bug where the `start` property of the `TASK` class will return the early finish date rather than early start date if task is not started. [Issue #1](https://github.com/jjCode01/xerparser/issues/1)

---

## 0.5.5 - 2023-01-21

### General Notes

* Added docstrings to more classes.
* Improved type validation.

### Added

* Added `full_code` property to `ACCOUNT` class. This property returns the full path to the cost code including any parent codes. This property is now the basis for comparing `ACCOUNT` objects.

## 0.5.4 - 2023-01-07

### General Notes

* Small amount of code cleanup and refactoring.

### Added  

* Added `parent_acct_id` and `seq_num` attributes to `ACCOUNT` class.
* Added `parent` property to `ACCOUNT` class.

---  

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
