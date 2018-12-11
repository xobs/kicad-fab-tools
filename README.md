# Kicad Fab Tools

Utilities for fabricating boards with KiCAD.

**pos2csv**: generate a pick-and-place .csv file from a KiCAD .pos file
**KiCadBomExport**: generate a usable BOM .csv file

## Creating a Pick-and-Place .csv File

Note: this is no longer necessary, as KiCad has the option to produce a "CSV"-formatted Position file now.

## Creating a BOM .csv file

In EESchema, go Tools -> Generate Bill of Materials.  Click "Add Plugin" and navigate to KiCadBomExport.py.  Modify the Command line to add -i and -o:

```
...KiCadBomExport.py" -i "%I" -o "%O"
```

Then click "Generate".

## Creating an assembly diagram

Install reportlab module.

Generate gerbers, including a CSV Pick-and-Place file.
Figure out the drill offset