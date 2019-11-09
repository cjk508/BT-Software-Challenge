Shortest Path Graph Search [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cjk508_Shortest-Path-Graph-Search&metric=alert_status)](https://sonarcloud.io/dashboard?id=cjk508_Shortest-Path-Graph-Search)
==========================

Software Challenge for an Assessment Centre

This program is written in Python using the sys and regex libraries provided as standard with Python.

There are 2 files, the program "employmentTree.py" and a test file "testDoc.txt" which is a slightly modified version of the original data

It is executed using the standard method, for Unix it is the following: 

```
python "employmentTree.py" *input text file* *First Employee Name* *Second Employee Name*
```

The text in astericks is required, however you will be prompted for them if you forget.

I have assumed that removed entries are entirely blank rows, if rows do have splits then false keys in the lookups are removed and badly formatted lines are skipped

If an employee ID appears more than once then the duplicate entry is skipped. This is something that should be a concern.

This algorithm does not deal with loops in management which hopefully should never happen
