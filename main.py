from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from utils import extract_lab_tests
from PIL import Image
import io

app = FastAPI()

@app.post("/get-lab-tests")
async def get_lab_tests(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        data = extract_lab_tests(image)
        return JSONResponse(content={"is_success": True, "data": data})
    except Exception as e:
        return JSONResponse(content={"is_success": False, "error": str(e)}, status_code=500)
