# Change Log  
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
