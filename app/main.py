# from fastapi import FastAPI, File, HTTPException, UploadFile
# import cv2
# import pytesseract
# import os
# from pdf2image import convert_from_path
# import platform
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

#         data = parse_document(text)

#         return {
#             "data": data,
#             "message": "Image processed successfully",
#             "processed_image": processed_path
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
#             filePath,
#             poppler_path=r"C:\Program Files\poppler\Library\bin"   # Change this to your Poppler path
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

# # def extract_text(image_path):
# #     result=reader.readtext(image_path)
# #     extracted_text=""
# #     for i in result:
# #         extract_text+=i[1]+"\n"
# #     return extract_text
# def extract_text(image_path):
#     text = pytesseract.image_to_string(image_path)
#     return text

# def parse_document(text):

#     return {
#         "raw_text": text
#     }

import cv2
import easyocr
import re

# Load EasyOCR model once
reader = easyocr.Reader(['en'], gpu=False)


def preprocess_image(image_path):
    """
    Preprocess image for better OCR.
    """

    image = cv2.imread(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return thresh


def extract_text(processed_image):
    """
    Extract text using EasyOCR.
    """

    result = reader.readtext(processed_image)

    text = ""

    for item in result:
        text += item[1] + "\n"

    return text


def parse_aadhaar(text):
    """
    Extract Aadhaar fields.
    """

    data = {
        "name": "",
        "dob": "",
        "gender": "",
        "aadhaar_number": "",
        "vid": "",
        "address": ""
    }

    # ---------------- DOB ----------------

    dob = re.search(r"\d{2}[/-]\d{2}[/-]\d{4}", text)

    if dob:
        data["dob"] = dob.group()

    # ---------------- Gender ----------------

    if "MALE" in text.upper():
        data["gender"] = "Male"

    elif "FEMALE" in text.upper():
        data["gender"] = "Female"

    # ---------------- Aadhaar ----------------

    aadhaar = re.search(r"\d{4}\s\d{4}\s\d{4}", text)

    if aadhaar:
        data["aadhaar_number"] = aadhaar.group().replace(" ", "")

    # ---------------- VID ----------------

    vid = re.search(
        r"VID\s*:?\s*(\d{4}\s\d{4}\s\d{4}\s\d{4})",
        text,
        re.IGNORECASE,
    )

    if vid:
        data["vid"] = vid.group(1).replace(" ", "")

    # ---------------- Name ----------------

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    for i, line in enumerate(lines):

        if "DOB" in line.upper():

            if i > 0:

                name = lines[i - 1]

                name = re.sub(r'[^A-Za-z ]', '', name)

                data["name"] = name.strip()

            break

    return data


def scan_document(image_path):
    """
    Complete OCR Pipeline
    """

    processed_image = preprocess_image(image_path)

    text = extract_text(processed_image)

    parsed_data = parse_aadhaar(text)

    return {
        "raw_text": text,
        "data": parsed_data
    }


# ---------------- Example ----------------

result = scan_document("aadhaar.jpg")

print(result)
