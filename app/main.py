# from fastapi import FastAPI, File, HTTPException, UploadFile
# import cv2
# import pytesseract
# import os
# from pdf2image import convert_from_path
# import platform
# import re
# if platform.system() == "Windows":
#     pytesseract.pytesseract.tesseract_cmd = (
#         r"C:\Users\Gayatri\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
#     )
#     print(pytesseract.get_tesseract_version())

# # reader=easyocr.Reader(['en'])#loads the model
# app = FastAPI(
#     title="Flutter Lens API",
#     version="1.0.0"
# )

# @app.get("/")
# def home():
#     return {    
#         "message": "Flutter Lens Backend Running"
#     }
# @app.post("/scanDoc")
# async def scan_document(file: UploadFile = File(...)):
#     try:
#         # Create uploads folder if it doesn't exist
#         os.makedirs("app/uploads", exist_ok=True)

#         contents = await file.read()

#         file_path = f"app/uploads/{file.filename}"

#         with open(file_path, "wb") as image:
#             image.write(contents)

#         processed_path = preprocessing_image(file_path)
#         text = extract_text(processed_path)
#         data = parse_aadhaar(text)
#         return {
#         "message": "Image processed successfully",
#         "processed_image": processed_path,
#         "raw_text": text,
#         "data": data
#         }

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )
# def preprocessing_image(filePath):

#     # Check if uploaded file is PDF
#     if filePath.lower().endswith(".pdf"):

#         pages = convert_from_path(
#             filePath
#         )

#         image_path = "app/uploads/page1.jpg"
#         pages[0].save(image_path, "JPEG")

#         image = cv2.imread(image_path)

#     else:
#         image = cv2.imread(filePath)

#     # OpenCV Processing
#     image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#     blur = cv2.GaussianBlur(gray, (5, 5), 0)

#     _, threshold = cv2.threshold(
#         blur,
#         0,
#         255,
#         cv2.THRESH_BINARY + cv2.THRESH_OTSU
#     )

#     processed_path = f"app/uploads/processed_{os.path.basename(filePath)}.jpg"

#     cv2.imwrite(processed_path, threshold)

#     return processed_path


# def extract_text(image_path):

#     image = cv2.imread(image_path)

#     text = pytesseract.image_to_string(image)

#     return text




# def parse_aadhaar(text):
#     result = {
#         "name": "",
#         "dob": "",
#         "gender": "",
#         "aadhaar_no": "",
#         "vid": "",
#     }

#     lines = []

#     for line in text.split("\n"):
#         line = line.strip()

#         if line != "":
#             lines.append(line)

#     # DOB
#     dob = re.search(r"\d{2}/\d{2}/\d{4}", text)
#     if dob:
#         result["dob"] = dob.group()

#     # Gender
#     if "FEMALE" in text.upper():
#         result["gender"] = "Female"
#     elif "MALE" in text.upper():
#         result["gender"] = "Male"

#     # Aadhaar Number
#     aadhaar = re.search(r"\d{4}\s\d{4}\s\d{4}", text)
#     if aadhaar:
#         result["aadhaar_no"] = aadhaar.group().replace(" ", "")

#     # VID
#     vid = re.search(r"VID\s*:?\s*(\d{4}\s\d{4}\s\d{4}\s\d{4})", text)
#     if vid:
#         result["vid"] = vid.group(1).replace(" ", "")

#     # Name (line before DOB)
#     for i in range(len(lines) - 2):

#         if "DOB" in lines[i + 1].upper():

#             if "MALE" in lines[i + 2].upper() or "FEMALE" in lines[i + 2].upper():

#                 result["name"] = lines[i]
#                 break

#     return result
import numpy as np
import cv2
import pytesseract
from pdf2image import convert_from_path
from fastapi.concurrency import run_in_threadpool

TESS_CONFIG = "--oem 1 --psm 6"
MAX_DIM = 1600   # cap — going bigger rarely improves accuracy but does slow things down a lot
MIN_DIM = 1000


def process_document(contents: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        tmp_pdf = os.path.join(UPLOAD_DIR, filename)
        with open(tmp_pdf, "wb") as f:
            f.write(contents)

        # dpi=150 is enough for OCR text recognition and is much cheaper
        # than 200-300+, especially on a dense two-language page like this one.
        pages = convert_from_path(tmp_pdf, dpi=150, first_page=1, last_page=1)
        image = cv2.cvtColor(np.array(pages[0]), cv2.COLOR_RGB2BGR)
    else:
        arr = np.frombuffer(contents, dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Could not decode image/PDF")

    image = resize_to_bounds(image)
    processed = preprocess_image(image)
    return pytesseract.image_to_string(processed, config=TESS_CONFIG)


def resize_to_bounds(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    longest = max(h, w)

    if longest > MAX_DIM:
        scale = MAX_DIM / longest
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    elif longest < MIN_DIM:
        scale = MIN_DIM / longest
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    return image


def preprocess_image(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return threshold