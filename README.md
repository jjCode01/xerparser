# xerparser

Read the contents of a P6 .xer file and convert it into a Python object.  

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

Do not pass the the .xer file directly as an argument to the `Xer` class. The file must be decoded and read into a string, which can then be passed as an argument. Or, pass the .xer file into the `Xer.reader` classmethod, which accepts:

* str or pathlib.Path objects for files stored locally or on a server.
* Binary files from requests, Flask, FastAPI, etc...

```python
from xerparser import Xer

file = r"/path/to/file.xer"
xer = Xer.reader(file)
```

<br/>

## Attributes

The tables stored in the .xer file are accessable as either Global, Project specific, Task specific, or Resource specific:

### Global

  ```python
  xer.export_info           # export data
  xer.activity_code_types   # dict of ACTVTYPE objects
  xer.activity_code_values  # dict of ACTVCODE objects
  xer.calendars             # dict of all CALENDAR objects
  xer.financial_periods     # dict of FINDATES objects
  xer.notebook_topics       # dict of MEMOTYPE objects
  xer.projects              # dict of PROJECT objects
  xer.project_code_types    # dict of PCATTYPE objects
  xer.project_code_values   # dict of PCATVAL objects
  xer.tasks                 # dict of all TASK objects
  xer.relationships         # dict of all TASKPRED objects
  xer.resources             # dict of RSRC objects
  xer.resource_rates        # dict of RSRCRATE objects
  xer.udf_types             # dict of UDFTYPE objects
  xer.wbs_nodes             # dict of all PROJWBS objects
  ```  

### Project Specific

```python
# Get first project
project = list(xer.projects.values())[0]

project.activity_codes        # list of project specific ACTVTYPE objects
project.calendars             # list of project specific CALENDAR objects
project.project_codes         # dict of PCATTYPE: PCATVAL objects
project.tasks                 # list of project specific TASK objects
project.relationships         # list of project specific TASKPRED objects
project.resources             # lest of project specific TASKRSRC objects
project.user_defined_fields   # dict of `UDFTYPE`: `UDF Value` pairs  
project.wbs_nodes             # list of project specific PROJWBS objects
```

### WBS Specific
```python
# Get projects root wbs node
wbs_node = project.wbs_root

wbs_node.children              # list of child PROJWBS objects
wbs_node.project               # PROJECT the WBS node belongs to
wbs_node.tasks                 # list of TASK objects assigned directly to WBS node
wbs_node.all_tasks             # list of TASK objects under the WBS node
wbs_node.user_defined_fields   # dict of `UDFTYPE`: `UDF Value` pairs  
```

### Task Specific

```python
# Get first task
task = project.tasks[0]

task.activity_codes       # dict of ACTVTYPE: ACTVCODE objects
task.memos                # list of TASKMEMO objects
task.periods              # list of TASKFIN objects
task.resources            # dict of TASKRSRC objects
task.user_defined_fields  # dict of `UDFTYPE`: `UDF Value` pairs 
```

### Resource Specific

```python
# Get first task resource
resource = list(task.resources.values())[0]

resource.periods              # list of TRSRCFIN objects
resource.user_defined_fields  # dict of `UDFTYPE`: `UDF Value` pairs 
```

<br/>

## Error Checking

Sometimes the xer file is corrupted during the export process. If this is the case, a `CorruptXerFile` Exception will be raised during initialization.  A list of the errors can be accessed from the `CorruptXerFile` Exception, or by using the `find_xer_errors` function.

### Option 1 - `errors` attribute of `CorruptXerFile` exception  (preferred)
```python
from xerparser import Xer, CorruptXerFile

file = r"/path/to/file.xer"
try:
    xer = Xer.reader(file)
except CorruptXerFile as e:
    for error in e.errors:
        print(error)
```  

### Option 2 - `find_xer_errors` function
```python
from xerparser import parser, file_reader, find_xer_errors

file = r"/path/to/file.xer"
xer_data = parser(file_reader(file))
file_errors = find_xer_errors(xer_data)
for error in file_errors:
    print(error)
```

### Errors

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
  | PCATVAL | PCATTYPE | *Project Code Data* |
  | PROJPCAT | PCATVAL | *Project Code Data* |
  | UDFVALUE | UDFTYPE | *User Defined Field Data* |

- Non-existent calendars assigned to tasks.
- Non-existent resources assigned to task resources.
