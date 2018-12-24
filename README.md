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

Install Python3, and install the reportlab module:

```sh
$ pip3 install reportlab
```

Generate gerbers, including a CSV Pick-and-Place file.
Figure out the drill offset.  This is the `aux_axis_origin 17.025 26.55` inside your kicad_pcb file:

```sh
$ grep aux_axis_origin *.kicad_pcb
    (aux_axis_origin 17.025 26.55)
$
```

Pass this along to `assygen.py`, along with any other parameters.  To get the full list, run `assygen.py -h`.

E.g.:

```sh
# Generate the Fomu assembly diagram.  Skip silk (since it doesn't exist), but include the fab layer (which does).
# The origin is at 17.025, 26.55.
# The PCB is small, so make the "assembly" boxes 0.1mm x 0.1mm.
python3 ./assygen.py hardware/releases/dvt1e/tomu-fpga -s -x 17.025 -y 26.55 -W 0.1 -H 0.1
```