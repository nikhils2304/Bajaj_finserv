import pytesseract
import re
from PIL import Image, ImageFilter

# Optional: set path to tesseract binary
# pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"  # Adjust as needed

def extract_lab_tests(image: Image.Image):
    # Preprocess the image: grayscale + threshold
    image = image.convert("L")
    image = image.point(lambda x: 0 if x < 140 else 255)
    image = image.filter(ImageFilter.SHARPEN)

    # OCR
    text = pytesseract.image_to_string(image)

    # Debug: print OCR output
    print("\n=== OCR OUTPUT ===\n", text)

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    test_data = []

    # Common lab test names (extend this list as needed)
    known_tests = [
        "HB", "RBC", "WBC", "SGOT", "SGPT", "ALKALINE PHOSPHATASE",
        "BILIRUBIN", "GLOBULIN", "ALBUMIN", "CREATININE", "TOTAL PROTEIN",
        "MCV", "MCH", "MCHC", "PCV", "HCT", "PLATELET", "NEUTROPHILS",
        "LYMPHOCYTES", "MONOCYTES", "EOSINOPHILS", "BASOPHILS", "SODIUM",
        "POTASSIUM", "CALCIUM", "GLUCOSE", "UREA", "CHOLESTEROL", "TRIGLYCERIDES"
    ]

    unit_corrections = {
        "gmdl": "g/dL",
        "mgdl": "mg/dL",
        "kul": "k/uL",
        "iu": "IU/L",
        "h": "",  # High indicator, not unit
        "l": "",  # Low indicator, not unit
    }

    pattern = re.compile(
        r"(?P<name>[A-Z ()/-]+?)\s+(?P<value>\d+\.?\d*)\s*"
        r"(?P<unit>[a-zA-Z/%]+)?\s*(?:\(?\s*(?P<range_low>\d+\.?\d*)\s*[-–]\s*(?P<range_high>\d+\.?\d*)\)?)?",
        re.IGNORECASE
    )

    for line in lines:
        match = pattern.search(line)
        if match:
            test_name = match.group("name").strip().upper()
            test_name = re.sub(r"[^A-Z0-9 ()/%-]", "", test_name)

            # Skip junk
            if len(test_name) < 3 or not any(key in test_name for key in known_tests):
                continue

            try:
                test_value = float(match.group("value"))
            except:
                continue

            test_unit = match.group("unit") or ""
            test_unit = re.sub(r"[^a-zA-Z/%]", "", test_unit).lower()
            test_unit = unit_corrections.get(test_unit, test_unit)

            ref_low = match.group("range_low")
            ref_high = match.group("range_high")

            if ref_low and ref_high:
                try:
                    ref_low = float(ref_low)
                    ref_high = float(ref_high)
                    out_of_range = not (ref_low <= test_value <= ref_high)
                    bio_range = f"{ref_low}-{ref_high}"
                except:
                    out_of_range = False
                    bio_range = ""
            else:
                out_of_range = False
                bio_range = ""

            test_data.append({
                "test_name": test_name,
                "test_value": str(test_value),
                "bio_reference_range": bio_range,
                "test_unit": test_unit,
                "lab_test_out_of_range": out_of_range
            })

    return test_data
