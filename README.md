# xerparser

A simple Python package that reads the contents of a P6 .xer file and converts it into a Python object.  

*Disclaimers:  
It's helpfull if you are already familiar with the mapping and schemas used by P6 during the export process.
Refer to the [Oracle Documentation]( https://docs.oracle.com/cd/F25600_01/English/Mapping_and_Schema/xer_import_export_data_map_project/index.htm) for more information regarding how data is mapped to the XER format.  
Tested on .xer files exported as versions 15.2 through 19.12.*  

<br/>

## Install

**Windows**:

```bash
pip install xerparser
```

**Linux/Mac**:

```bash
pip3 install xerparser
```

<br/>  

## Usage  

Import the `Xer` class from `xerparser`  and pass the contents of a .xer file as an argument. Use the `Xer` class variable `CODEC` to set the proper encoding to decode the file.

```python
from xerparser import Xer

file = r"/path/to/file.xer"
with open(file, encoding=Xer.CODEC, errors="ignore") as f:
    file_contents = f.read()
xer = Xer(file_contents)
```

*Note: do not pass the the .xer file directly as an argument. The file must be decoded and read into a string, which can then be passed as an argument.*  

<br/>

## Attributes

The tables stored in the .xer file are accessable as either Global , Project specific, Task specific, or Resource specific:

### Global

  ```python
  xer.export_info           # export data
  xer.errors                # list of potential errors in export process
  xer.activity_code_types   # dict of ACTVTYPE objects
  xer.activity_code_values  # dict of ACTVCODE objects
  xer.calendars             # dict of all CALENDAR objects
  xer.financial_periods     # dict of FINDATES objects
  xer.notebook_topics       # dict of MEMOTYPE objects
  xer.projects              # dict of PROJECT objects
  xer.tasks                 # dict of all TASK objects
  xer.relationships         # dict of all TASKPRED objects
  xer.resources             # dict of RSRC objects
  xer.wbs_nodes             # dict of all PROJWBS objects
  ```  

### Project Specific

```python
# Get first project
project = xer.projects.values()[0]

project.activity_codes  # list of project specific ACTVTYPE objects
project.calendars       # list of project specific CALENDAR objects
project.tasks           # list of project specific TASK objects
project.relationships   # list of project specific TASKPRED objects
project.wbs_nodes       # list of project specific PROJWBS objects
```

### Task Specific

```python
# Get first task
task = project.tasks[0]

task.activity_codes   # dict of ACTVTYPE: ACTVCODE objects
task.memos            # list of TASKMEMO objects
task.resources        # dict of TASKRSRC objects
task.periods          # list of TASKFIN objects
```

### Resource Specific

```python
# Get first task resource
resource = task.resources.values()[0]

resource.periods  # list of TRSRCFIN objects
```

<br/>

## Error Checking

Sometimes the xer file is corrupted during the export process. A list of potential errors is generated based on common issues encountered when analyzing .xer files:  

- Minimum required tables - an error is recorded if one of the following tables is missing:
  - CALENDAR
  - PROJECT
  - PROJWBS
  - TASK
  - TASKPRED  
- Required table pairs - an error is recorded if Table 1 is included but not Table 2:  
  
  | Table 1       | Table 2       | Notes    |
  | :----------- |:-------------|----------|
  | TASKFIN | FINDATES | *Financial Period Data for Task* |
  | TRSRCFIN | FINDATES | *Financial Period Data for Task Resource* |
  | TASKRSRC | RSRC | *Resource Data* |
  | TASKMEMO | MEMOTYPE | *Notebook Data* |
  | ACTVCODE | ACTVTYPE | *Activity Code Data* |
  | TASKACTV | ACTVCODE | *Activity Code Data* |

- Non-existent calendars assigned to activities.
