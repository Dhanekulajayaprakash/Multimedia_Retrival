from PIL import Image
from paddleocr import PaddleOCR

_ocr_model = None

def get_ocr_model():
    global _ocr_model
    if _ocr_model is None:
        print("Loading PaddleOCR model...")
        _ocr_model = PaddleOCR(
            use_doc_orientation_classify=True,
            use_doc_unwarping=True,
            use_textline_orientation=True,
            enable_mkldnn=False,
        )
    return _ocr_model

def ocr(image_path:str):
    model = get_ocr_model()
    result = model.predict(image_path)
    text = "\n".join(result[0]["rec_texts"])
    return text