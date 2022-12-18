# xerparser

A simple Python package that reads a P6 .xer file and converts it into a Python object.  
<br>
*Disclaimers:  
This package is only usefull if you are already familiar with the mapping and schemas used by P6 during the export process. 
Refer to the [Oracle Documentation]( https://docs.oracle.com/cd/F25600_01/English/Mapping_and_Schema/xer_import_export_data_map_project/index.htm) for more information regarding how data is mapped to the XER format.  
Tested on .xer files exported as versions 15.2 through 19.12.*  
<br>
## Install
**Windows**:
```bash
pip install xerparser
```
**Linux/Mac**: 
```bash
pip3 install xerparser
```
<br>  

## Usage  
Import the ***Xer*** class from **xerparser**  and pass a .xer file as an argument.  
```python
from xerparser import Xer

file = r"/path/to/file.xer"
xer = Xer(file)
```
The Xer class accepts .xer file passed as types **str**, **path**, or **bytes**.  
The file and table data will be parsed and returned as a Python object.  
<br>
## Attributes 
The tables stored in the .xer file are attributes for the **Xer** class. Since a XER file can contain multiple projects/schedules, the tables are accessable as either Global , Project specific, or Task Specific:
###  Global
  ```python
  xer.export    # export data
  xer.errors    # list of potential errors in export process
  xer.calendars # dict of CALENDAR objects
  xer.projects  # dict of PROJECT objects
  xer.resources # dict of RSRC objectrs
  ```  
### Project Specific
```python
# Get first project
project = xer.projects.values()[0]

project.calendars       # set of CALENDAR objects used by project
project.tasks           # dict of TASK objects
project.relationships   # dict of TASKPRED objects
project.wbs             # dict of PROJWBS objects
```
### Task Specific
```python
# Get first task
task = project.tasks.values()[0]

task.memos        # list of TASKMEMO objects
task.resources    # list of TASKRSRC objects
```
### Error Checking
Sometimes the xer file is corrupted during the export process. A list of potential errors is generated based on common issues encountered when analyzing .xer files:  
- Minimum required tables - an error is recorded if one of the following tables is missing:
  - CALENDAR
  - PROJECT
  - PROJWBS
  - TASK
  - TASKPRED  
- Required table pairs - an error is recorded if Table 1 is included but not Table 2:  
  
  | P6 Table 1       | P6 Table 2       | Notes    |
  | :----------- |:-------------|----------|
  | TASKFIN | FINDATES | *Financial Period Data for Task* |
  | TRSRCFIN | FINDATES | *Financial Period Data for Task Resource* |
  | TASKRSRC | RSRC | *Resource Data* |
  | TASKMEMO | MEMOTYPE | *Notebook Data* |
  | ACTVCODE | ACTVTYPE | *Activity Code Data* |
  | TASKACTV | ACTVCODE | *Activity Code Data* |

- Non-existent calendars assigned to activities.

<br>  

## Example Code
```python
from xerparser import Xer, PROJECT

file = r"/path/to/file.xer"
xer = Xer(file)  
xer.export.version  # -> 15.2  
xer.export.date  # -> datetime.datetime(2022, 11, 30, 0, 0)  
xer.errors  # -> []  

# get first project
project: PROJECT = xer.projects.values()[0]

# get project name
project.name

# get project data date
project.data_date

# get project finish date
project.finish_date

# get task and relationship count
len(project.tasks)
len(project.relationships)

# loop through tasks
for task in project.tasks.values():
    print(task)

```