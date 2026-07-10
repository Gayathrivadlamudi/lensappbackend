from fastapi import FastAPI, File, HTTPException, UploadFile
import cv2
import pytesseract
import os
from pdf2image import convert_from_path
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Gayatri\AppData\Local\Programs\Tesseract-OCR"
# reader=easyocr.Reader(['en'])#loads the model
app = FastAPI(
    title="Flutter Lens API",
    version="1.0.0"
)

@app.get("/")
def home():
    return {    
        "message": "Flutter Lens Backend Running"
    }
@app.post("/scanDoc")
async def scan_document(file: UploadFile = File(...)):
    try:
        # Create uploads folder if it doesn't exist
        os.makedirs("app/uploads", exist_ok=True)

        contents = await file.read()

        file_path = f"app/uploads/{file.filename}"

        with open(file_path, "wb") as image:
            image.write(contents)

        processed_path = preprocessing_image(file_path)

        text = extract_text(processed_path)

        data = parse_document(text)

        return {
            "data": data,
            "message": "Image processed successfully",
            "processed_image": processed_path
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
def preprocessing_image(filePath):

    # Check if uploaded file is PDF
    if filePath.lower().endswith(".pdf"):

        pages = convert_from_path(
            filePath,
            poppler_path=r"C:\Program Files\poppler\Library\bin"   # Change this to your Poppler path
        )

        image_path = "app/uploads/page1.jpg"
        pages[0].save(image_path, "JPEG")

        image = cv2.imread(image_path)

    else:
        image = cv2.imread(filePath)

    # OpenCV Processing
    image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    _, threshold = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    processed_path = f"app/uploads/processed_{os.path.basename(filePath)}.jpg"

    cv2.imwrite(processed_path, threshold)

    return processed_path

# def extract_text(image_path):
#     result=reader.readtext(image_path)
#     extracted_text=""
#     for i in result:
#         extract_text+=i[1]+"\n"
#     return extract_text
def extract_text(image_path):
    text = pytesseract.image_to_string(image_path)
    return text

def parse_document(text):

    return {
        "raw_text": text
    }
