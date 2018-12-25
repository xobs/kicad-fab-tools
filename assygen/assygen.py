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
                (ax, ay) = canv.absolutePosition(j.xc - j.w/2, j.yc-j.h/2)
                # print("Item Rect: ({}, {}) ({}, {}) -- ({}, {})".format(j.xc - j.w/2, j.yc-j.h/2, j.w, j.h,
                #                                                         ax, ay))
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
            (ax, ay) = canv.absolutePosition(20 * mm, yt,)
            # print("Legend Rect: ({}, {}) ({}, {}) -- ({}, {})".format(20 *
            #                                                           mm, yt, 10 * mm, 3 * mm, ax, ay))
            canv.rect(20 * mm, yt, 10 * mm, 3 * mm, 1, 1)
            canv.setFillGray(0)
            n = n+1
            for part in group:
                dsgn = dsgn + " " + part.name
            canv.drawString(120 * mm, yt, dsgn)
            canv.drawString(40 * mm, yt, group[0].ref[0:20])
            canv.drawString(80 * mm, yt, group[0].desc[0:20])


class PickAndPlaceFileKicad(PickAndPlaceFile):
    def __init__(self, fname, **kwargs):
        xOffset = kwargs.get('xOffset', 0)
        yOffset = kwargs.get('yOffset', 0)
        componentWidth = kwargs.get('componentWidth', 1)
        componentHeight = kwargs.get('componentHeight', 1)

        reader = csv.reader(open(fname, 'r'))
        rows = []
        for row in reader:
            rows.append(row)

        self.col_map = [
            colors.Color(1, 0, 0),
            colors.Color(1, 1, 0),
            colors.Color(0, 1, 0),
            colors.Color(0, 1, 1),
            colors.Color(1, 0, 1),
            colors.Color(0, 0, 1),
        ]

        i_dsg = rows[0].index("Ref")
        i_desc = rows[0].index("Val")
        i_cx = rows[0].index("PosX")
        i_cy = rows[0].index("PosY")
        i_layer = rows[0].index("Side")

        self.layers = {}
        self.layers["Top"] = {}
        self.layers["Bottom"] = {}

        # print(i_dsg, i_desc, i_cx, i_cy)
        for i in rows[1:]:
            if len(i) > 0:
                cx = (float(i[i_cx]) + float(xOffset)) * mm
                cy = (float(i[i_cy]) - float(yOffset)) * mm

                if "DNP" in i[i_desc]:
                    print("Skipping component {} because it's DNP".format(i[i_desc]))
                    continue
                w = componentWidth * mm
                h = componentHeight * mm
                l = i[i_layer]
                if l == "top":
                    layer = "Top"
                else:
                    layer = "Bottom"
                ref = i[i_desc]
                if(not ref in self.layers[layer]):
                    self.layers[layer][ref] = []
                self.layers[layer][ref].append(PPComponent(
                    cx, cy, w, h, i[i_dsg], i[i_desc], ref))
        # print(self.layers)


def renderGerber(base_name, layer, canv, **kwargs):
    global gerberExtents

    def getFileName(base, side, title, side_ext, ext):
        from pathlib import Path
        for proto in [
            base + '-' + side + '.' + title + '.g' + side_ext + ext,
            base + '-' + side + '.' + title + '.gbr',
        ]:
            if Path(proto).is_file():
                return proto
        raise 'Unable to find ' + title + ' file'

    if layer == "Bottom":
        side = 'B'
        side_ext = 'b'
    else:
        side = 'F'
        side_ext = 't'

    canv.setLineWidth(0.0)
    gm = GerberMachine("", canv)
    gm.Initialize()
    ResetExtents()

    extents = [0, 0, 0, 0]

    if kwargs['renderCopper']:
        f = getFileName(base_name, side, 'Cu', side_ext, 'l')
        gm.setColors(colors.Color(0.85, 0.85, 0.85), colors.Color(0, 0, 0))
        extents = gm.ProcessFile(f)

    if kwargs['renderFab']:
        f = getFileName(base_name, side, 'Fab', side_ext, 'f')
        gm.setColors(colors.Color(0.25, 0.25, 0.25), colors.Color(0, 0, 0))
        extents = gm.ProcessFile(f)

    if kwargs['renderSilk']:
        f = getFileName(base_name, side, 'SilkS', side_ext, 'o')
        gm.setColors(colors.Color(0.5, 0.5, 0.5), colors.Color(0, 0, 0))
        extents = gm.ProcessFile(f)

    return extents


def producePrintoutsForLayer(base_name, layer, canv, **kwargs):
    print("Rendering assembly file to {}".format(base_name + '_assy.pdf'))
    ctmp = canvas.Canvas(base_name + "_assy.pdf")
    ext = renderGerber(base_name, layer, ctmp, **kwargs)

    scale_x = (gerberPageSize[0]-2*gerberMargin)/((ext[2]-ext[0]))
    scale_y = (gerberPageSize[1]-2*gerberMargin)/((ext[3]-ext[1]))
    scale = min(scale_x, scale_y)
    gerberScale = (scale, scale)
    # print(
    #     "Gerber range: ({}, {}) -> ({}, {})".format(ext[0], ext[1], ext[2], ext[3]))
    # print("PS", gerberPageSize[0], gerberMargin, gerberScale)
    gerberOffset = (-ext[0] + (gerberMargin / scale),
                    -ext[1] + (gerberMargin / scale))
    # print("Offset: (%4.2f, %4.2f)" % gerberOffset)
    # print("Scale (in.):  (%4.2f, %4.2f)" % gerberScale)

    from pathlib import Path
    pnp_filename = None
    for proto_filename in [
        base_name + '-all-pos.csv',
        base_name + '-' + layer.lower() + '-pos.csv',
    ]:
        if Path(proto_filename).is_file():
            pnp_filename = proto_filename
    if pnp_filename is None:
        raise 'Unable to find component pick-and-place file'

    pf = PickAndPlaceFileKicad(pnp_filename, **kwargs)
    ngrp = pf.num_groups(layer)

    for page in range(0, int((ngrp+5)/6)):
        n_comps = min(6, ngrp - page*6)

        canv.saveState()
        if layer == 'Bottom':
            # For the bottom layer, flip the canvas horizontally
            # in order to make the silk readable.
            canv.scale(-1, 1)
            canv.scale(gerberScale[0], gerberScale[1])
            canv.translate(2*gerberOffset[0], gerberOffset[1])
            pass
        else:
            canv.scale(gerberScale[0], gerberScale[1])
            canv.translate(gerberOffset[0], gerberOffset[1])

        renderGerber(base_name, layer, canv, **kwargs)

        pf.draw(layer, page*6, n_comps, canv)
        canv.restoreState()

        pf.gen_table(layer, page*6, n_comps, canv)
        canv.showPage()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Create an assembly document from KiCad gerber files',
        epilog='You almost certainly will have to specify -x and -y.  Look for the "aux_axis_origin" definition in your .kicad_pcb file to get the origin information.  \n\n'
        + "The componentWidth and componentHeight will be scaled to match your PCB.  If your PCB is 1x1mm, then the dots will be _very_ large.")
    parser.add_argument('-x', '--xOffset', metavar='MM', type=float, default=0,
                        help='X offset of the auxiliary access (aux_axis_origin from .kicad_pcb)')
    parser.add_argument('-y', '--yOffset', metavar='MM', type=float, default=0,
                        help='Y offset of the auxiliary access (aux_axis_origin from .kicad_pcb)')
    parser.add_argument('-W', '--componentWidth', metavar='MM', type=float, default=1,
                        help='Width of the "Place Here" marker, in mm')
    parser.add_argument('-H', '--componentHeight', metavar='MM', type=float, default=1,
                        help='Height of the "Place Here" marker, in mm')
    parser.add_argument('-f', '--fab', action='store_true',
                        help='Render the "Fab" layer')
    parser.add_argument('-s', '--silk', action='store_false',
                        help='Don\'t render the "Silk" layer')
    parser.add_argument('-c', '--copper', action='store_false',
                        help='Don\'t render the "Copper" layer')
    parser.add_argument('prefix')
    args = parser.parse_args()

    canv = canvas.Canvas(args.prefix + "_assy.pdf")
    producePrintoutsForLayer(args.prefix, "Top", canv,
                             xOffset=args.xOffset, yOffset=args.yOffset,
                             componentWidth=args.componentWidth, componentHeight=args.componentHeight,
                             renderFab=args.fab,
                             renderSilk=args.silk,
                             renderCopper=args.copper)
    producePrintoutsForLayer(args.prefix, "Bottom", canv,
                             xOffset=args.xOffset, yOffset=args.yOffset,
                             componentWidth=args.componentWidth, componentHeight=args.componentHeight,
                             renderFab=args.fab,
                             renderSilk=args.silk,
                             renderCopper=args.copper)
    canv.save()
