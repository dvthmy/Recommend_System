# 📋 TỔNG QUAN LOGIC ĐỒNG BỘ HỆ THỐNG RECOMMENDATION

## 🔐 1. AUTHENTICATION FLOW (Sign In / Sign Up / Guest)

### 1.1 Sign Up Flow
**Frontend:** `frontend/src/components/Auth.tsx`
- User nhập: username, password, confirmPassword, age, gender
- Validation: kiểm tra password match, age hợp lệ
- Gọi API: `apiService.signUp()`
- Backend: `backend/api/routers/auth.py` → `/auth/signup`
  - Hash password bằng SHA256
  - Kiểm tra username đã tồn tại
  - Tạo User node trong Neo4j với default values:
    - `locale: "vi-VN"`
    - `skill_level: "beginner"`
    - `max_cook_time: 60`
    - `meal_preferences: []`
  - Tạo JWT token
  - Trả về UserProfile + access_token
- Frontend lưu: `userId` và `access_token` vào localStorage
- Navigate: `/onboarding`

### 1.2 Sign In Flow
**Frontend:** `frontend/src/components/Auth.tsx`
- User nhập: username, password
- Gọi API: `apiService.signIn()`
- Backend: `backend/api/routers/auth.py` → `/auth/signin`
  - Hash password và so sánh với database
  - Tạo JWT token mới
  - Trả về UserProfile + access_token
- Frontend lưu: `userId` và `access_token` vào localStorage
- Navigate: `/` (Home)

### 1.3 Guest Flow
**Frontend:** `frontend/src/components/Auth.tsx`
- User click "Continue as Guest"
- Gọi API: `apiService.createUser()`
- Backend: `backend/api/routers/users.py` → `POST /users`
  - Tạo User node với `user_id` random (format: `user_{uuid}`)
  - Default values giống Sign Up
  - **Backup ngay lập tức** vào `backend/data/users/user_backup.json`
- Frontend lưu: `userId` vào localStorage (không có token)
- Navigate: `/onboarding`

### 1.4 User Initialization (App Start)
**Frontend:** `frontend/src/contexts/UserContext.tsx` → `initializeUser()`
- Kiểm tra localStorage: `userId` và `access_token`
- Nếu có cả 2:
  - Verify token: `apiService.verifyToken()`
  - Nếu token valid: Load user profile
  - Nếu token invalid: Thử refresh token
  - Nếu refresh fail: Clear tokens, yêu cầu sign in lại
- Nếu chỉ có `userId` (guest):
  - Load user profile
  - Nếu không tìm thấy: **KHÔNG tự động tạo** (chỉ tạo khi user click "Continue as Guest")
- Nếu không có gì: User chưa đăng nhập

---

## 📝 2. ONBOARDING / SURVEY FLOW

**Frontend:** `frontend/src/components/Onboarding.tsx`

### 2.1 Các bước Onboarding:
1. **Ingredient Allergies (Optional)**
   - Search ingredients: Gọi `apiService.searchIngredients()`
   - User có thể thêm custom ingredients (ID: `custom-{timestamp}`)
   - Lưu vào state `selectedAllergies`
   - **Chỉ hiển thị nếu:** `!allergies || allergies.allergies.length === 0`

2. **Favorite Cuisines (Required)**
   - Chọn tối đa 5 cuisines từ danh sách có sẵn
   - Lưu vào state `preferences.favoriteCuisines`
   - **Chỉ hiển thị nếu:** `!favoriteCuisines || favoriteCuisines.favorite_cuisines.length === 0`

3. **Meal Types (Required)**
   - Dropdown chọn 1 meal type (breakfast, lunch, dinner, etc.)
   - Lưu vào state `preferences.preferredMealTypes`

4. **Cooking Time (Required)**
   - Slider từ 0-180 phút
   - Map minutes → preference ID (quick/fast/medium/slow/very_slow)
   - Lưu vào state `preferences.cookingTimePreference`

### 2.2 Submit Onboarding:
**Function:** `finishOnboarding()`
1. Update user profile:
   - `max_cook_time`: từ cooking time preference
   - `locale: "vi-VN"`
   - `skill_level: "intermediate"`
   - Gọi: `updateUserProfile(user_id, profileUpdate)`

2. Add allergies (nếu có):
   - Gọi: `apiService.addUserAllergies(user_id, { ingredient_ids })`
   - Backend: Tạo relationship `(User)-[:ALLERGIC_TO]->(Ingredient)`

3. Add favorite cuisines (nếu có):
   - Gọi: `apiService.addUserFavoriteCuisine()` cho mỗi cuisine
   - Backend: Tạo relationship `(User)-[:FAVORS_CUISINE {preference_level: 5}]->(Cuisine)`

4. Reload data:
   - `loadUserAllergies()`
   - `loadUserFavoriteCuisines()`

5. Save preferences vào localStorage: `userPreferences`
6. Navigate: `/suggestions`

---

## 🥘 3. INPUT INGREDIENTS & RECOMMENDATION FLOW

**Frontend:** `frontend/src/components/FoodSuggestions.tsx`

### 3.1 Input Ingredients - Manual
- Search ingredients: Gọi `apiService.searchIngredients()` (debounce 300ms)
- User có thể:
  - Chọn từ dropdown (từ search results hoặc available ingredients)
  - Thêm custom ingredient (ID: `custom-{timestamp}`)
- Lưu vào state `selectedIngredients`
- **Lưu vào localStorage:** `uploadedIngredients` (array of `{id, name}`)
- **Load từ localStorage:** Khi component mount, load saved ingredients

### 3.2 Input Ingredients - Upload Image
- User upload image → Modal mở
- Gọi API: `apiService.detectIngredients([file])`
- Backend: `backend/api/routers/detect.py` → `POST /detect`
  - Sử dụng Google Gemini AI (`gemini-2.5-flash`)
  - Prompt: Nhận diện edible ingredients trong ảnh
  - Trả về: `{ ingredients: string[] }`
- Frontend match detected names với `availableIngredients`:
  - Exact match
  - Partial match (contains)
  - Word-based match
- Thêm matched ingredients vào `selectedIngredients`
- Lưu vào localStorage

### 3.3 Get Recommendations
**Function:** `loadRecommendations()`
- Chỉ chạy khi user click button "Get Suggestions"
- Gọi API: `apiService.getRecommendations(request)`
- Request:
  ```typescript
  {
    user_id: user.user_id,
    ingredient_ids: selectedIngredients.length > 0 ? selectedIngredients : undefined,
    max_cook_time: user.max_cook_time,
    limit: 10
  }
  ```
- Backend: `backend/api/routers/recommend.py` → `POST /recommend`
  - Gọi `recommender.py` → `GraphHybridRecommender.recommend()`
  - Logic recommendation:
    - Nếu có `user_id`: Personalized recommendations (dựa trên interactions, allergies, favorite cuisines)
    - Nếu có `ingredient_ids`: Filter recipes có chứa ingredients
    - Tính Jaccard similarity
    - Filter theo `max_cook_time`
    - Filter theo `recipe_category` (meal type)
    - Priority ranking theo `preferred_cuisines`
    - Trả về top N recipes với match score
- Frontend hiển thị:
  - Match score (%)
  - Recipe details (title, cuisine, cook time, image, etc.)

---

## 👁️ 4. VIEW INTERACTION

**Frontend:** `frontend/src/components/FoodDetail.tsx`

### 4.1 Record View
- Khi component mount:
  - Kiểm tra `sessionStorage.getItem('viewed_{recipeId}')`
  - Nếu chưa xem: Set flag và gọi `loadRecipeDetail(id, recordView=true)`
  - Nếu đã xem: Gọi `loadRecipeDetail(id, recordView=false)`

- Trong `loadRecipeDetail()`:
  - Load recipe detail từ API
  - Nếu `recordView=true`:
    - Gọi: `apiService.recordUserInteraction(userId, { recipe_id, event_type: 'view' })`

### 4.2 Backend View Logic
**Backend:** `backend/api/routers/interactions.py`
- Tạo/Update relationship: `(User)-[:INTERACTED_WITH]->(Recipe)`
- View logic:
  ```cypher
  // Chỉ count view nếu:
  // - Chưa từng xem HOẶC
  // - Lần xem trước cách đây > 5 giây
  WHERE rel.last_view IS NULL OR 
        duration.inSeconds(last_view, datetime()).seconds > 5
  SET rel.event_type = 'view',
      rel.last_view = datetime(),
      rel.view_count = coalesce(rel.view_count, 0) + 1,
      r.popularity_views = coalesce(r.popularity_views, 0) + 1
  ```
- Trả về: `{ message, user_view_count, recipe_total_views }`

---

## ❤️ 5. LIKE INTERACTION

### 5.1 Frontend - FoodSuggestions
- User click "Rate" button → Mở rating modal
- User chọn rating (1-5 stars)
- Submit: `apiService.recordUserInteraction(userId, { recipe_id, event_type: 'like', rating })`

### 5.2 Frontend - FoodDetail
- User click "Rate this dish"
- Gọi: `apiService.recordUserInteraction(userId, { recipe_id, event_type: 'like', rating: 5 })`

### 5.3 Backend Like Logic
**Backend:** `backend/api/routers/interactions.py`
- Kiểm tra: Đã liked chưa?
  ```cypher
  MATCH (u:User)-[rel:INTERACTED_WITH]->(r:Recipe)
  RETURN rel.liked AS liked
  ```
- Nếu đã liked: Trả về `{ message: "Already liked ❤️", liked: true }`
- Nếu chưa liked:
  ```cypher
  SET rel.event_type = 'like',
      rel.liked = true,
      rel.like_time = datetime(),
      rel.timestamp = datetime()
  WITH r
  SET r.popularity_likes = coalesce(r.popularity_likes, 0) + 1
  ```
- Trả về: `{ message: "Liked ❤️", liked: true, recipe_likes }`

---

## ⭐ 6. RATING INTERACTION

### 6.1 Frontend
- **FoodSuggestions:** Rating modal với 5 stars
- **FoodDetail:** "Rate this dish" button (hiện tại hardcode rating=5)
- Gọi: `apiService.recordUserInteraction(userId, { recipe_id, event_type: 'rating', rating: 1-5 })`

### 6.2 Backend Rating Logic
**Backend:** `backend/api/routers/interactions.py`
- Validation: `rating` required, phải trong khoảng 1-5
- Update relationship:
  ```cypher
  SET rel.event_type = 'rating',
      rel.rating = $rating,
      rel.rating_time = datetime(),
      rel.timestamp = datetime()
  ```
- Update recipe aggregate:
  ```cypher
  WITH r, collect(rel.rating) AS all_ratings
  SET r.rating_count = size(all_ratings),
      r.rating_value = round(reduce(total=0, x IN all_ratings | total + x) / size(all_ratings), 2)
  ```
- Trả về: `{ message, user_rating, recipe_avg_rating, rating_count }`

---

## 💾 7. SAVING INTERACTION

### 7.1 Frontend
- **FoodDetail:** "Add to favorites" button
- Gọi: `apiService.recordUserInteraction(userId, { recipe_id, event_type: 'save' })`
- **Lưu ý:** Backend hiện tại chưa xử lý `event_type: 'save'` riêng, có thể dùng `like` thay thế

### 7.2 Backend (Cần implement)
- Tương tự like, nhưng set `rel.saved = true`
- Update `r.popularity_saves`

---

## 📊 8. HISTORY & PROFILE

### 8.1 History Page
**Frontend:** `frontend/src/components/History.tsx`
- Tabs: Liked, Rated, Saved
- Load interactions:
  - Gọi: `apiService.getUserInteractions(userId, event_type, limit, offset)`
  - Backend: `GET /users/{user_id}/interactions`
    - Trả về: `{ likes: [], views: [], ratings: [] }`
- Với mỗi interaction, load recipe detail để hiển thị

### 8.2 Profile Page
**Frontend:** `frontend/src/components/Profile.tsx`
- Hiển thị:
  - User info (username, age, gender)
  - Favorite cuisines (từ `favoriteCuisines`)
  - Allergies (từ `allergies`)
  - Activity stats:
    - Liked recipes count
    - Saved recipes count
    - Rated recipes count
- Load stats:
  - Gọi: `apiService.getUserInteractionStats(userId)`
  - Backend: `GET /users/{user_id}/interactions/stats`
    - Trả về: `{ stats: { like_count, view_count, rating_count, save_count } }`
- Edit profile:
  - Modal để edit allergies và favorite cuisines
  - Add/Remove allergies: `addUserAllergies()`, `removeUserAllergies()`
  - Add/Remove cuisines: `addUserFavoriteCuisine()`, `removeUserFavoriteCuisine()`

---

## 🔄 9. DATA SYNCHRONIZATION

### 9.1 LocalStorage
- `userId`: User ID
- `access_token`: JWT token (chỉ có khi sign in/sign up)
- `uploadedIngredients`: Array of `{id, name}` (ingredients đã chọn)
- `userPreferences`: User preferences object
- `foodRatings`: Object `{recipeId: rating}`

### 9.2 SessionStorage
- `viewed_{recipeId}`: Flag để tránh count view nhiều lần trong cùng session

### 9.3 Backend Backup
- **Location:** `backend/data/users/user_backup.json`
- **Khi nào backup:**
  - Khi tạo user mới (guest)
  - Khi update user profile
  - Khi add/remove allergies
  - Khi add/remove favorite cuisines
- **Format:**
  ```json
  {
    "user_id": {
      "profile": { ...user properties },
      "relations": {
        "ALLERGIC_TO": ["ingredient_id1", ...],
        "DISLIKES": [],
        "FAVORS_CUISINE": ["cuisine_name1", ...]
      }
    }
  }
  ```
- **Auto-restore:** Khi get user profile mà không tìm thấy, tự động restore từ backup

### 9.4 Neo4j Relationships
- `(User)-[:ALLERGIC_TO]->(Ingredient)`
- `(User)-[:DISLIKES]->(Ingredient)`
- `(User)-[:FAVORS_CUISINE {preference_level}]->(Cuisine)`
- `(User)-[:INTERACTED_WITH {event_type, view_count, liked, rating, last_view, like_time, rating_time, timestamp}]->(Recipe)`
- `(Recipe)-[:HAS_INGREDIENT]->(Ingredient)`

---

## 🎯 10. RECOMMENDATION ALGORITHM

**Backend:** `backend/scripts/recommend_graph.py` → `GraphHybridRecommender`

### 10.1 Input Parameters
- `user_id`: Optional, để personalize
- `ingredient_ids`: Optional, filter recipes có chứa ingredients
- `ingredient_names`: Optional, sẽ map sang IDs
- `max_cook_time`: Filter theo cooking time
- `recipe_category`: Filter theo meal type
- `preferred_cuisines`: Priority ranking
- `limit`: Số lượng kết quả
- `min_match_ratio`: Jaccard similarity threshold (default: 0.6)

### 10.2 Recommendation Logic
1. **Ingredient Matching:**
   - Tính Jaccard similarity giữa user ingredients và recipe ingredients
   - Filter: `jaccard >= min_match_ratio`

2. **User Personalization (nếu có user_id):**
   - Load user allergies → Exclude recipes có allergic ingredients
   - Load user favorite cuisines → Boost score cho recipes có matching cuisines
   - Load user interactions → Boost score cho recipes đã like/rate cao

3. **Filtering:**
   - `max_cook_time`: Filter recipes có `total_time_min <= max_cook_time`
   - `recipe_category`: Filter theo meal type

4. **Ranking:**
   - Jaccard similarity score
   - Cuisine preference boost
   - Interaction history boost
   - Popularity (views, likes) boost

5. **Return:**
   - Top N recipes với match score (0-100%)

---

## ⚠️ 11. ERROR HANDLING & FALLBACKS

### 11.1 Network Errors
- Frontend catch network errors → Hiển thị error message
- Fallback: Load mock data nếu API fail

### 11.2 User Not Found
- Nếu có token: Clear session, yêu cầu sign in lại
- Nếu không có token (guest): Tự động restore từ backup hoặc tạo mới

### 11.3 API Failures
- Recommendation API fail → Load mock suggestions
- Interaction API fail → Log error, không block UI
- Profile load fail → Hiển thị error, cho phép retry

---

## 🔑 12. KEY FILES REFERENCE

### Frontend
- `frontend/src/components/Auth.tsx` - Authentication
- `frontend/src/components/Onboarding.tsx` - Survey/Onboarding
- `frontend/src/components/FoodSuggestions.tsx` - Input ingredients & recommendations
- `frontend/src/components/FoodDetail.tsx` - Recipe detail & interactions
- `frontend/src/components/History.tsx` - User activity history
- `frontend/src/components/Profile.tsx` - User profile & preferences
- `frontend/src/contexts/UserContext.tsx` - User state management
- `frontend/src/services/api.ts` - API service layer

### Backend
- `backend/api/routers/auth.py` - Authentication endpoints
- `backend/api/routers/users.py` - User management & preferences
- `backend/api/routers/recommend.py` - Recommendation endpoint
- `backend/api/routers/interactions.py` - Interaction endpoints (view/like/rating)
- `backend/api/routers/detect.py` - Image ingredient detection
- `backend/api/services/recommender.py` - Recommendation service
- `backend/scripts/recommend_graph.py` - Graph-based recommendation algorithm

---

## 📝 NOTES

1. **Guest users** không có JWT token, chỉ có `userId` trong localStorage
2. **View counting** có debounce 5 giây để tránh spam
3. **Like** chỉ set một lần, không toggle
4. **Rating** có thể update nhiều lần (ghi đè)
5. **Saving** hiện tại chưa được implement riêng, có thể dùng `like` thay thế
6. **Backup system** tự động restore user nếu bị mất trong Neo4j
7. **Custom ingredients** (ID bắt đầu bằng `custom-`) không được lưu vào database, chỉ trong localStorage

