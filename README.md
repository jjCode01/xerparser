# xerparser

A simple Python package that reads a P6 .xer file and converts it into a Python dictionary object.  
<br>
*Disclaimer: this package is only usefull if you are already familiar with the mapping and schemas used by P6 during the export process. 
Refer to the [Oracle Documentation]( https://docs.oracle.com/cd/F25600_01/English/Mapping_and_Schema/xer_import_export_data_map_project/index.htm) for more information regarding how data is mapped to the XER format.*  
<br>
## Install
**Windows**: pip install xerparser  
**Linux/Mac**: pip3 install xerparser  
<br>
## Usage
```python
xer_to_dict(file: str | bytes) -> dict
```  
Import the ***xer_to_dict*** function from **xerparser**  and pass a .xer file as an argument.  
```python
from xerparser import xer_to_dict

file = r"/path/to/file.xer"
xer = xer_to_dict(file)
```
The xer_to_dict function accepts .xer file passed as type **str** or type **bytes**.  
The file and table data will be parsed and returned as a Python dictionary object contining the file and table data from the .xer.  
<br>
## Keys / Attributes 
**\["version"]** -> Version of P6 the .xer file was exported as.  <br>
**\["export_date"]** -> Date the .xer file was exported from P6 (datetime object).  
**\["errors"]** -> A list of potential errors in the .xer file based on common issues encountered when analyzing .xer files:  
- Minimum required tables - an error is recorded if one of the following tables is missing:
  - CALENDAR
  - PROJECT
  - PROJWBS
  - TASK
  - TASKPRED  
- Required table pairs - an error is recorded if Table 1 is included but not Table 2:  
  
  | P6 Table 1       | P6 Table 2       | Notes    |
  | :-----------: |:-------------:|----------|
  | TASKFIN | FINDATES | *Financial Period Data for Task* |
  | TRSRCFIN | FINDATES | *Financial Period Data for Task Resource* |
  | TASKRSRC | RSRC | *Resource Data* |
  | TASKMEMO | MEMOTYPE | *Notebook Data* |
  | ACTVCODE | ACTVTYPE | *Activity Code Data* |
  | TASKACTV | ACTVCODE | *Activity Code Data* |

- Non-existent calendars assigned to activities.
<br>  
  
**\["tables"]**: Dictionay of each table included in the .xer file.  
Examples: *PROJECT, PROJWBS, CALENDAR, TASK, TASKPRED*, etc...  
The table name (e.g *TASK*) is the key, and the value is a list of the table entries, which can be accessed the same as any Python dictionary object:  
    
```python
xer["tables"]["TASK"]
# or
xer["tables"].get("TASK")
```  

Each table entry is a dictionary object where the key is the field name (e.g. *task_id, task_code, and task_name*) from the table schema.

```python
for task in xer["tables"].get["TASK", []]:  
    print(task["task_code"], task["task_name"])  # -> A1000 Install Widget
```  
<br>  

## Example Code
```python
from xerparser import xer_to_dict  

file = r"/path/to/file.xer"
xer = xer_to_dict(file)  
xer["version"]  # -> 15.2  
xer["export_date"]  # -> datetime.datetime(2022, 11, 30, 0, 0)  
xer["errors"]  # -> []  

xer["tables"].get("TASK")  # -> [{"task_id": 12345, ...}, {"task_id": 12346,...}]  
len(xer["tables"].get("TASK",[]))  # -> 950
```