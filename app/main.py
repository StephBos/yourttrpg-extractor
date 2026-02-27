from PIL import Image
from typing import List
import pymupdf
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from .models import Block
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"

app = FastAPI(title="TTRPG Extraction Service")

#TODO: implement endpoint here
@app.post("/extract")
async def extractRules(file: UploadFile = File(...)):
    """Extract text from uploaded PDF file"""
    print(f"Extracting rules from: {file.filename}")

    try:
        # Extract text
        pdf_bytes = await file.read()
        blocks = buildBlocksFromPdf(pdf_bytes)
        print("Blocks extracted:", blocks)

        return {"blocks": blocks}
    except Exception as e:
        # print full traceback so you can see what went wrong in the logs
        import traceback
        traceback.print_exc()
        # it’s generally more useful to raise an HTTPException instead of
        # returning a JSONResponse yourself; this keeps status codes clear
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

#TODO: Build blocks from pdf
def buildBlocksFromPdf(pdf_bytes: bytes) -> List[Block]:
    """
    Very basic block builder for now.
    Later you replace this with header-scored layout grouping.
    """
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    
    print("doc", doc)

    blocks: List[Block] = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text()
        
        if not text.strip():
            text = getTextUsingOCR(page)
        # VERY naive block creation:
        # For now treat each page as one block
        blocks.append(
            Block(
                title=f"Page {page_number}",
                content=text,
                page_start=page_number,
                page_end=page_number
            )
        )

    return blocks

def getTextUsingOCR(page) -> str:
    """Fallback OCR method for pages with no extractable text"""
    print("Attempting OCR for page with no text...")
    try:
        # Render page to a pixmap
        pix = page.get_pixmap()
        print("we got a pixmap", pix)
        imgpdf = pix.pdfocr_tobytes()
        print("we got an ocr pdf", imgpdf)
        text = imgpdf.get_text()

        print('text', text)
        return text
    except Exception as e:
        # log the failure and re‑raise so the caller can handle it
        print("OCR error:", repr(e))
        raise

#TODO: Extract rules from blocks

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
