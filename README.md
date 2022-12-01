# `xerparser`

`xerparser` reads a P6 .xer file and converts it into a Python dictionary object containing key, value pairs:
1. ***"version"***: Version of P6 the .xer file was exported as.
2. ***"export_date"***: Date the .xer file was exported from P6 (datetime object).
3. ***"errors"***: A list of potential errors in the .xer file based on common issues encountered when analyzing .xer files:  
    - Minimum required tables for a valid P6 schedule are:
      - CALENDAR
      - PROJECT
      - PROJWBS
      - TASK
      - TASKPRED
    - Required table pairs are:
      - TASKFIN <> FINDATES : (*Financial Period Data*)
      - TRSRCFIN <> FINDATES (*Financial Period Data*)
      - TASKRSRC <> RSRC (*Resource Data*)
      - TASKMEMO <> MEMOTYPE (*Notebook Data*)
      - ACTVCODE <> ACTVTYPE (*Activity Code Data*)
      - TASKACTV <> ACTVCODE (*Activity Code Data*)
    - Non-existent calendars assigned to activities.  
    <br>
4. ***"tables"***: Dictionay of each table included in the .xer file.  
    Examples: *PROJECT, PROJWBS, CALENDAR, TASK, TASKPRED*, etc... [See Oracle Documentation]( https://docs.oracle.com/cd/F25600_01/English/Mapping_and_Schema/xer_import_export_data_map_project/index.htm) for mapping and schema of P6 database tables.  
    The table name (e.g *TASK*) is the key, and the value is a list of the table entries, which can be accessed the same as any Python dictionary object:  
    
    >xer["tables"]["TASK"]  
    >or  
    >xer["tables"].get("TASK")  

   Each table entry is a dictionary object where the key is the field name (e.g. *task_id, task_code, and task_name*) from the table schema.

   >for task in xer["tables"].get["TASK", []]:  
   >&nbsp;&nbsp;&nbsp;&nbsp; print(task["task_code"], task["task_name"])

Example Code
>from P6XerParser import xer_to_dict  
>
>xer = xer_to_dict("*path to file.xer*")  
>xer["version"]  # -> *15.2*  
>xer["export_date"]  # -> *datetime.datetime(2022, 11, 30, 0, 0)*  
>xer["errors"]  # -> *[ ]*  
>
>xer["tables"].get("TASK")  # -> *[{"task_id": 12345, ...}, {"task_id": 12346,...}]*  
>len(xer["tables"].get("TASK",[]))  # -> *950* 