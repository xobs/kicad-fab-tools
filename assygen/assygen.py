#!/usr/bin/env python3

from gerber2pdf import *
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import csv


class PPComponent:
    def __init__(self, xc, yc, w, h, name, desc, ref):
        self.xc = xc
        self.yc = yc
        self.w = w
        self.h = h
        if(self.w == 0):
            self.w = 0.8 * mm

        if(self.h == 0):
            self.h = 0.8 * mm

        self.name = name
        self.desc = desc
        self.ref = ref


class PickAndPlaceFile:
    def split_parts(self, layer, index, n_comps):
        parts = []
        n = 0
        for i in sorted(self.layers[layer].keys()):
            if(n >= index and n < index+n_comps):
                parts.append(self.layers[layer][i])
            n = n+1
        return parts

    def num_groups(self, layer):
        return len(self.split_parts(layer, 0, 10000))

    def draw(self, layer, index, n_comps, canv):
        parts = self.split_parts(layer, index, n_comps)
        n = 0
        for i in parts:
            canv.setStrokeColor(self.col_map[n])
            canv.setFillColor(self.col_map[n])
            n = n+1
            for j in i:
                (ax, ay)=canv.absolutePosition(j.xc - j.w/2, j.yc-j.h/2)
                print("Item Rect: ({}, {}) ({}, {}) -- ({}, {})".format(j.xc - j.w/2, j.yc-j.h/2, j.w, j.h,
                    ax, ay))
                canv.rect(j.xc - j.w/2, j.yc-j.h/2, j.w, j.h, 1, 1)

    def gen_table(self, layer, index, n_comps, canv):
        parts = self.split_parts(layer, index, n_comps)

        yt = 260 * mm
        canv.setFont("Helvetica", 10)
        canv.setStrokeGray(0)
        canv.setFillGray(0)
        canv.drawString(20 * mm, yt, "Color")
        canv.drawString(40 * mm, yt, "Lib.Reference")
        canv.drawString(80 * mm, yt, "Comment")
        canv.drawString(120 * mm, yt, "Designators")
        n = 0
        for group in parts:
            dsgn = ""
            yt = yt - 6 * mm
            canv.setFillColor(self.col_map[n])
            (ax, ay)=canv.absolutePosition(20 * mm, yt,)
            print("Legend Rect: ({}, {}) ({}, {}) -- ({}, {})".format(20 * mm, yt, 10 * mm, 3 * mm, ax, ay))
            canv.rect(20 * mm, yt, 10 * mm, 3 * mm, 1, 1)
            canv.setFillGray(0)
            n = n+1
            for part in group:
                dsgn = dsgn + " " + part.name
            canv.drawString(120 * mm, yt, dsgn)
            canv.drawString(40 * mm, yt, group[0].ref[0:20])
            canv.drawString(80 * mm, yt, group[0].desc[0:20])

#            table.append(["", dsgn, group[0].desc, group[0].ref])


# class PickAndPlaceFileKicad(PickAndPlaceFile):
#     def __init__(self, fname):
#         print("Load")
#         f = open(fname, 'r')
#         rows = []
#         for line in f:
#             rows.append(line.strip().split(','))

#         self.col_map = [colors.Color(1, 0, 0),
#                         colors.Color(1, 1, 0),
#                         colors.Color(0, 1, 0),
#                         colors.Color(0, 1, 1),
#                         colors.Color(1, 0, 1),
#                         colors.Color(0, 0, 1)]

# #	Ref    Val                  Package         PosX       PosY        Rot     Side

#         i_dsg = rows[0].index("Ref")
#         i_desc = rows[0].index("Val")
#         i_cx = rows[0].index("PosX")
#         i_cy = rows[0].index("PosY")
#         i_layer = rows[0].index("Side")

#         self.layers = {}
#         self.layers["Top"] = {}
#         self.layers["Bottom"] = {}

#         print(i_dsg, i_desc, i_cx, i_cy)
#         for i in rows[1:]:
#             if(len(i) > 0):
#                 print(i[i_dsg], i[i_cx])
#                 cx = float(i[i_cx]) * mm
#                 cy = float(i[i_cy]) * mm

#                 w = 1 * mm
#                 h = 1 * mm
#                 l = i[i_layer]
#                 if l == "top":
#                     layer = "Top"
#                 else:
#                     layer = "Bottom"
#                 ref = i[i_desc]
# #                print(ref,cy, py)
#                 if(not ref in self.layers[layer]):
#                     self.layers[layer][ref] = []
#                 self.layers[layer][ref].append(PPComponent(
#                     cx, cy, w, h, i[i_dsg], i[i_desc], ref))
#         print(self.layers)

class PickAndPlaceFileKicad(PickAndPlaceFile):
    def __init__(self, fname, **kwargs):
        xOffset = kwargs.get('xOffset', 0)
        yOffset = kwargs.get('yOffset', 0)
        componentWidth = kwargs.get('componentWidth', 1)
        componentHeight = kwargs.get('componentHeight', 1)

        reader = csv.reader(open(fname,'r'))
        rows = []
        for row in reader:
            rows.append(row)

        self.col_map = [
            colors.Color(1,0,0),
            colors.Color(1,1,0),
            colors.Color(0,1,0),
            colors.Color(0,1,1),
            colors.Color(1,0,1),
            colors.Color(0,0,1),
        ]

        i_dsg = rows[0].index("Ref")
        i_desc = rows[0].index("Val")
        i_cx = rows[0].index("PosX")
        i_cy = rows[0].index("PosY")
        i_layer = rows[0].index("Side")

        self.layers = {}
        self.layers["Top"] = {}
        self.layers["Bottom"] = {}

        print(i_dsg, i_desc, i_cx, i_cy)
        for i in rows[1:]:
            if(len(i) > 0):
                # print(i[i_dsg], i[i_cx])
                cx = (float(i[i_cx]) + float(xOffset)) * mm
                cy = (float(i[i_cy]) - float(yOffset)) * mm

                w = componentWidth * mm
                h = componentHeight * mm
                l = i[i_layer]
                if l == "top":
                    layer = "Top"
                else:
                    layer = "Bottom"
                ref = i[i_desc]
#                print(ref,cy, py)
                if(not ref in self.layers[layer]):
                    self.layers[layer][ref] = []
                self.layers[layer][ref].append(PPComponent(
                    cx, cy, w, h, i[i_dsg], i[i_desc], ref))
        print(self.layers)

def renderGerber(base_name, layer, canv):
    global gerberExtents
    if(layer == "Bottom"):
        # f_copper = base_name+"-B.Cu.gbr"
        # f_overlay = base_name+"-B.SilkS.gbr"
        f_copper = base_name+"-B.Cu.gbl"
        f_overlay = base_name+"-B.SilkS.gbo"
    else:
        # f_copper = base_name+"-F.Cu.gbr"
        # f_overlay = base_name+"-F.SilkS.gbr"
        f_copper = base_name+"-F.Cu.gtl"
        f_overlay = base_name+"-F.SilkS.gto"

    canv.setLineWidth(0.0)
    gm = GerberMachine("", canv)
    gm.Initialize()
    ResetExtents()
    gm.setColors(colors.Color(0.85, 0.85, 0.85), colors.Color(0, 1, 0))
    gm.ProcessFile(f_copper)
    gm.setColors(colors.Color(0.5, 0.5, 0.5), colors.Color(1, 0, 0))
    return gm.ProcessFile(f_overlay)


def producePrintoutsForLayer(base_name, layer, canv, **kwargs):

    ctmp = canvas.Canvas(base_name + "_assy.pdf")
    ext = renderGerber(base_name, layer, ctmp)

    scale_x = (gerberPageSize[0]-2*gerberMargin)/((ext[2]-ext[0]))
    scale_y = (gerberPageSize[1]-2*gerberMargin)/((ext[3]-ext[1]))
    scale = min(scale_x, scale_y)
    gerberScale = (scale, scale)
    print("Gerber range: ({}, {}) -> ({}, {})".format(ext[0], ext[1], ext[2], ext[3]))
    print("PS" , gerberPageSize[0], gerberMargin, gerberScale)
    gerberOffset = (-ext[0] + (gerberMargin / scale), -ext[1] + (gerberMargin / scale))
    # gerberOffset = (-ext[0], -ext[1])
    print("Offset (in.): (%4.2f, %4.2f)" % (gerberOffset[0]/inch, gerberOffset[1]/inch))
    print("Scale (in.):  (%4.2f, %4.2f)" % gerberScale)

    pf = PickAndPlaceFileKicad(base_name+'-' + layer.lower() + '-pos.csv', **kwargs)
    ngrp = pf.num_groups(layer)

    for page in range(0, int((ngrp+5)/6)):
        n_comps = min(6, ngrp - page*6)

        canv.saveState()
        canv.scale(gerberScale[0], gerberScale[1])
        canv.translate(gerberOffset[0], gerberOffset[1])
        if layer == 'Bottom':
            # print("Translating canvas again: ({}, {})".format(0.5*gerberPageSize[0], 0))
            # canv.translate(0.5*gerberPageSize[0],0)
            # print("Scaling canvas again: ({}, {})".format(-1, 1))
            # canv.scale(-1, 1)
            # print("Translating canvas yet again: ({}, {})".format(-0.75*gerberPageSize[0], 0))
            # canv.translate(-0.75*gerberPageSize[0],0)
            pass
#        else:
#            canv.scale(gerberScale[0], gerberScale[1])

        renderGerber(base_name, layer, canv)

        pf.draw(layer, page*6, n_comps, canv)
        canv.restoreState()

        pf.gen_table(layer, page*6, n_comps, canv)
        canv.showPage()

if __name__ == "__main__":
    import sys
    import argparse
    xOffset = 17.05
    yOffset = 26.475
    canv = canvas.Canvas(sys.argv[1]+"_assy.pdf")
    producePrintoutsForLayer(sys.argv[1], "Top", canv, xOffset=xOffset, yOffset=yOffset)
    producePrintoutsForLayer(sys.argv[1], "Bottom", canv, xOffset=xOffset, yOffset=yOffset, componentWidth=0.2, componentHeight=0.2)
    canv.save()
