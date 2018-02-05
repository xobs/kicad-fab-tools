# Kicad Fab Tools

Utilities for fabricating boards with KiCAD.

**pos2csv**: generate a pick-and-place .csv file from a KiCAD .pos file
**KiCadBomExport**: generate a usable BOM .csv file

## Creating a Pick-and-Place .csv File

Create a .pos file from PCBNew.  File -> Fabrication Outputs -> Footprint Position (.pos) File.  Check One File Per Board.

Then use node to convert the file into a csv file:

```
node pos2csv.js input.pos output.csv
```

## Creating a BOM .csv file

In EESchema, go Tools -> Generate Bill of Materials.  Click "Add Plugin" and navigate to KiCadBomExport.py.  Modify the Command line to add -i and -o:

```
...KiCadBomExport.py" -i "%I" -o "%O"
```

Then click "Generate".