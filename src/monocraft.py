# Monocraft, a monospaced font for developers who like Minecraft a bit too much.
# Copyright (C) 2022-2023 Idrees Hassan
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import json
import math
import os

import fontforge

from polygonizer import PixelImage, generatePolygons

PIXEL_SIZE = 150

characters = json.load(open("./characters.json", encoding="utf8"))

charactersByCodepoint = {}

def generateFont():
    monocraft = fontforge.font()
    monocraft.fontname = "Monocraft"
    monocraft.familyname = "Monocraft"
    monocraft.fullname = "Monocraft"
    monocraft.copyright = "Idrees Hassan, https://github.com/IdreesInc/Monocraft"
    monocraft.encoding = "UnicodeFull"
    monocraft.version = "3.0"
    monocraft.weight = "Regular"
    monocraft.em = 1050
    monocraft.ascent = 750
    monocraft.descent = 300
    monocraft.upos = -PIXEL_SIZE  # Underline position
    monocraft.addLookup("ligatures", "gsub_ligature", (), (("liga", (("dflt", ("dflt")), ("latn", ("dflt")))),))
    monocraft.addLookupSubtable("ligatures", "ligatures-subtable")

    for character in characters:
        charactersByCodepoint[character["codepoint"]] = character
        monocraft.createChar(character["codepoint"], character["name"])
        pen = monocraft[character["name"]].glyphPen()
        width = len(character["pixels"][0]) + 1 if "pixels" in character else 6
        name = character["name"]

        image, kw = generateImage(character)
        drawImage(image, pen, **kw)
        monocraft[name].width = PIXEL_SIZE * width
    print(f"Generated {len(characters)} characters")

    outputDir = "../dist/"
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    monocraft.generate(outputDir + "Monocraft.ttf")


def generateImage(character):
    image = PixelImage()
    kw = {}
    arr = character["pixels"]
    descent = -character["descent"] if "descent" in character else 0
    y = math.floor(descent)
    kw['dy'] = descent - y
    image = image | imageFromArray(arr, 0, y)

    return image, kw


def findHighestY(image):
    for y in range(image.y_end - 1, image.y, -1):
        for x in range(image.x, image.x_end):
            if image[x, y]:
                return y
    return image.y


def imageFromArray(arr, x=0, y=0):
    return PixelImage(
        x=x,
        y=y,
        width=len(arr[0]),
        height=len(arr),
        data=bytes(x for a in reversed(arr) for x in a),
    )


def drawImage(image, pen, *, dx=0, dy=0):
    for polygon in generatePolygons(image):
        start = True
        for x, y in polygon:
            x = (x + dx) * PIXEL_SIZE
            y = (y + dy) * PIXEL_SIZE
            if start:
                pen.moveTo(x, y)
                start = False
            else:
                pen.lineTo(x, y)
        pen.closePath()


generateFont()