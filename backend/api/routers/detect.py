from fastapi import APIRouter, UploadFile, File
import google.generativeai as genai
from PIL import Image
import tempfile, os, time

# ✅ Khởi tạo router
router = APIRouter(prefix="/detect", tags=["Detection"])

# ✅ Cấu hình API key Gemini
#genai.configure(api_key="AIzaSyAlaSpeltP5wniCnzbygZVGUUyVSct3bw0")

genai.configure(api_key="YOUR_API_KEY_HERE")

# ✅ Prompt nhận dạng nguyên liệu
PROMPT = """
You are a precise food ingredient recognition model.

Your goal is to identify every visible *edible ingredient* in the given image.

**Instructions:**
- Focus only on edible food ingredients and seasonings.
- Ignore utensils, plates, labels, and backgrounds.
- Distinguish between similar white powders (salt, sugar, flour).
- Include both major and minor items (spices, condiments, herbs, oils).
- Output: lowercase, comma-separated ingredient names.
"""

@router.post("/")   # ✅ chỉ cần "/"
async def detect(files: list[UploadFile] = File(...)):
    all_ingredients = set()

    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        try:
            # ✅ Mở ảnh trong context manager
            with Image.open(tmp_path) as img:
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content([PROMPT, img])

                if response.text:
                    text = response.text.strip().lower()
                    ingredients = [x.strip() for x in text.split(",") if x.strip()]
                    all_ingredients.update(ingredients)
                else:
                    print(f"⚠️ No text detected for {file.filename}")

        except Exception as e:
            print(f"❌ Lỗi khi xử lý ảnh {file.filename}: {e}")

        finally:
            try:
                os.remove(tmp_path)
            except Exception as e:
                print(f"⚠️ Không thể xóa file tạm {tmp_path}: {e}")

    return {"ingredients": sorted(list(all_ingredients))}
