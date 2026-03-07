from PIL import Image
import pymupdf
from fastapi import FastAPI, UploadFile, File
from models.Block import Block
import logging
import os
import pytesseract

logger = logging.getLogger(__name__)

def extract_page_lines(page):
    layout = page.get_text("dict")
    lines = []

    for block in layout["blocks"]:
        if "lines" not in block:
            continue

        for line in block["lines"]:
            text = ""
            max_size = 0
            is_bold = False

            for span in line["spans"]:
                text += span["text"]
                max_size = max(max_size, span["size"])

                if "Bold" in span["font"]:
                    is_bold = True

            text = text.strip()

            if text:
                lines.append({
                    "text": text,
                    "size": max_size,
                    "bold": is_bold,
                    "y": line["bbox"][1]
                })

    return lines


def extract_lines_with_ocr(page):

    pix = page.get_pixmap(dpi=300)

    img = Image.frombytes(
        "RGB",
        (pix.width, pix.height),
        pix.samples
    )

    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    lines = []
    current_line = ""

    for i, word in enumerate(data["text"]):
        if not word.strip():
            continue

        current_line += word + " "
        logger.info('data: ' + str(data))
        if data["line_num"][i] != data["line_num"][i-1] if i > 0 else False:
            lines.append({
                "text": current_line.strip(),
                "size": 10,
                "bold": False,
                "y": data["top"][i]
            })
            current_line = ""
        logger.info(f"Final line: {current_line.strip()}")

    return lines


def is_header(line):


    if line["size"] >= 14:
        return True

    if line["bold"] and len(line["text"]) < 60:
        return True

    return False


def detect_block_type(title, content):

    t = title.lower()
    c = content.lower()

    if "casting time:" in c and "range:" in c:
        return "spell"

    if "hit points" in c and "armor class" in c:
        return "monster"

    if "table" in t:
        return "table"

    if "level" in t and "feature" in c:
        return "class_feature"

    if "prerequisite:" in c:
        return "feat"

    return "rule"


def buildBlocksFromPdf(pdf_bytes: bytes) -> list[Block]:

    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    blocks = []
    current_block = None

    for page_number, page in enumerate(doc, start=1):

        text = page.get_text()

        if len(text.strip()) < 50:
            logger.info('No text found on page, using OCR')
            lines = extract_lines_with_ocr(page)
        else:
            logger.info('Text found on page, using text extraction')
            lines = extract_page_lines(page)

        for line in lines:

            if is_header(line):

                if current_block:
                    current_block.type = detect_block_type(
                        current_block.title,
                        current_block.content
                    )
                    blocks.append(current_block)

                current_block = Block(
                    title=line["text"],
                    content="",
                    page_start=page_number,
                    page_end=page_number
                )

            else:

                if not current_block:
                    current_block = Block(
                        title="Introduction",
                        content="",
                        page_start=page_number,
                        page_end=page_number
                    )

                current_block.content += line["text"] + "\n"

    if current_block:
        current_block.type = detect_block_type(
            current_block.title,
            current_block.content
        )
        blocks.append(current_block)

    return blocks