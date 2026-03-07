from PIL import Image
import pymupdf
from fastapi import FastAPI, UploadFile, File
from models.Block import Block
import logging
import os
import pytesseract
from extracion.blocks import extract_page_lines, extract_lines_with_ocr, is_header, detect_block_type, buildBlocksFromPdf


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/5/tessdata/'

app = FastAPI(title="TTRPG Extraction Service")

@app.post("/extract")
async def extractRules(file: UploadFile = File(...)):
    logger.info(f"Extracting rules from: {file.filename}")

    try:
        pdf_bytes = await file.read()
        blocks = buildBlocksFromPdf(pdf_bytes)
        logger.info(f"Extracted blocks: {blocks}")
        logger.info(f"Blocks extracted: {len(blocks)}")

        return {"blocks": blocks}
    except Exception as e:
        logger.error(f"Error during extraction: {repr(e)}")
        import traceback
        traceback.print_exc()
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "good"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
