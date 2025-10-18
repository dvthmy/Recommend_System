// 1. Seed popularity data cho recipes
MATCH (r:Recipe)
WITH r, rand() AS r1, rand() AS r2, rand() AS r3, rand() AS r4
SET r.popularity_views = toInteger(100 + floor(r1 * 5000)),
    r.popularity_saves = toInteger(10 + floor(r2 * 500)),
    r.popularity_cooks = toInteger(5 + floor(r3 * 200)),
    r.popularity_likes = toInteger(20 + floor(r4 * 800))
RETURN count(r) AS recipes_updated;

// 2. Tạo interaction history cho user u_1
MATCH (u:User {user_id: 'u_1'})
MATCH (r:Recipe) 
WHERE r.recipe_id IN ['rec_46', 'rec_56', 'rec_87', 'rec_116', 'rec_143', 'rec_3', 'rec_4', 'rec_5']
WITH u, r, rand() AS rand_val,
     CASE 
       WHEN rand_val < 0.3 THEN 'cook'
       WHEN rand_val < 0.6 THEN 'save' 
       ELSE 'view'
     END AS event_type,
     datetime() - duration({days: toInteger(rand() * 30)}) AS timestamp
MERGE (u)-[iv:INTERACTED_WITH]->(r)
SET iv.event_type = event_type,
    iv.timestamp = timestamp,
    iv.rating = CASE WHEN event_type = 'cook' THEN toFloat(3.5 + rand() * 1.5) ELSE null END
RETURN count(iv) AS interactions_created;
