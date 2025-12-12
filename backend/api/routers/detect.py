from fastapi import APIRouter, UploadFile, File
import google.generativeai as genai
from PIL import Image
import tempfile, os, time

# ✅ Khởi tạo router
router = APIRouter(prefix="/detect", tags=["Detection"])

# ✅ Cấu hình API key Gemini từ biến môi trường
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCQgmvzZ3KMa9Z3rJvq2qU7phTi4X9LTR4")
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Prompt nhận dạng nguyên liệu
PROMPT = """
You are an expert food ingredient recognition system connected to a structured ingredient database.

Your job is to identify ONLY edible ingredients visible in the image and express them in their canonical ingredient names.

━━━━━━━━━━
STRICT INSTRUCTIONS
━━━━━━━━━━
1. Focus only on edible ingredients. Ignore utensils, packaging, plates, hands, napkins, decorations, labels, logos, or background items.
2. Use generic ingredient names that exist in a structured ingredient table (e.g., "beef", "chicken breast", "carrot", "garlic", "olive oil", "soy sauce").
3. Remove preparation descriptors — no "chopped", "fresh", "sliced", "raw", "cooked", "fried", "steamed", "boiled", "grilled", "shredded".
4. Remove quantity and adjectives unless they change the ingredient identity.
   ❗ Keep: "brown sugar", "black pepper", "red onion", "coconut milk"
5. Distinguish visually similar items with the most likely identity:
   - sugar vs salt vs flour
   - scallion vs chive
   - mozzarella vs cheddar
6. Include minor ingredients: herbs, oils, seasonings, sauces, condiments, garnishes, spices, seeds, nuts.
7. If an ingredient appears multiple times, list it only once.
8. NEVER return:
   - brand names (e.g., Heinz, Kikkoman, Oreo)
   - recipe names (e.g., spaghetti bolognese, fried rice, ramen)
   - general categories (e.g., vegetables, spices, meat)
9. Pick the most statistically likely ingredient if uncertain between similar items.
10. Your output MUST follow the strict format rules below.

━━━━━━━━━━
OUTPUT FORMAT (REQUIRED)
━━━━━━━━━━
- Only ingredient names
- All lowercase
- Comma-separated
- No bullets or numbering
- No sentences or explanations
- No units or quantities
- No adjectives for texture/state (sliced / raw / cooked / grilled / shredded)

━━━━━━━━━━
NORMALIZATION EXAMPLES
━━━━━━━━━━
- "garlic cloves", "minced garlic" → garlic
- "fried egg", "scrambled eggs" → egg
- "soy sauce bottle" → soy sauce
- "extra virgin olive oil" → olive oil
- "basil leaves" → basil
- "brown sugar" → sugar (unless "brown sugar" is visually obvious)
- "grilled chicken breast", "roast chicken" → chicken

━━━━━━━━━━
FINAL EXPECTED OUTPUT EXAMPLE
━━━━━━━━━━
garlic, olive oil, egg, chicken, onion, soy sauce, black pepper

Respond ONLY with the comma-separated ingredient list and nothing else.
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
