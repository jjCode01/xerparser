# Change Log  
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
