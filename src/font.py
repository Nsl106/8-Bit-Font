import json
import math
import os

import fontforge

from generate_diacritics import generateDiacritics
from polygonizer import PixelImage, generatePolygons

PIXEL_SIZE = 150

characters = json.load(open("./characters.json", encoding="utf8"))
diacritics = json.load(open("./diacritics.json"))

characters = generateDiacritics(characters, diacritics)
charactersByCodepoint = {}

def generateFont():
    font = fontforge.font()
    font.fontname = "T9432"
    font.familyname = "T9432"
    font.fullname = "T9432"
    font.copyright = "Nolan Locke, https://github.com/Nsl106/8-Bit-Font"
    font.encoding = "UnicodeFull"
    font.version = "3.0"
    font.weight = "Regular"
    font.em = 1050
    font.ascent = 750
    font.descent = 300
    font.upos = -PIXEL_SIZE  # Underline position
    font.addLookup("ligatures", "gsub_ligature", (), (("liga", (("dflt", ("dflt")), ("latn", ("dflt")))),))
    font.addLookupSubtable("ligatures", "ligatures-subtable")

    for character in characters:
        charactersByCodepoint[character["codepoint"]] = character
        font.createChar(character["codepoint"], character["name"])
        pen = font[character["name"]].glyphPen()
        width = len(character["pixels"][0]) + 1 if "pixels" in character else 6
        name = character["name"]

        image, kw = generateImage(character)
        drawImage(image, pen, **kw)
        font[name].width = PIXEL_SIZE * width
    print(f"Generated {len(characters)} characters")

    outputDir = "../dist/"
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    font.generate(outputDir + "T9432.ttf")


def generateImage(character):
    image = PixelImage()
    kw = {}

    if "pixels" in character:
        arr = character["pixels"]
        descent = -character["descent"] if "descent" in character else 0
        y = math.floor(descent)
        kw['dy'] = descent - y
        image = image | imageFromArray(arr, 0, y)

    if "reference" in character:
        other = generateImage(charactersByCodepoint[character["reference"]])
        kw.update(other[1])
        image = image | other[0]

    if "diacritic" in character:
        diacritic = diacritics[character["diacritic"]]
        arr = diacritic["pixels"]
        x = image.x
        y = findHighestY(image) + 1
        if "diacriticSpace" in character:
            y += int(character["diacriticSpace"])
        image = image | imageFromArray(arr, x, y)

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