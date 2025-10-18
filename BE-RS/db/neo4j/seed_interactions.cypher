// 1. Seed popularity data cho recipes
MATCH (r:Recipe)
WITH r, rand() AS r1, rand() AS r2, rand() AS r3, rand() AS r4
SET r.popularity_views = toInteger(100 + floor(r1 * 5000)),
    r.popularity_saves = toInteger(10 + floor(r2 * 500)),
    r.popularity_cooks = toInteger(5 + floor(r3 * 200)),
    r.popularity_likes = toInteger(20 + floor(r4 * 800));

// 2. Tạo cook interactions cho user u_1
MATCH (u:User {user_id: 'u_1'})
MATCH (r:Recipe) 
WHERE r.recipe_id IN ['rec_46', 'rec_56', 'rec_87']
WITH u, r, datetime() - duration({days: toInteger(rand() * 30)}) AS timestamp
MERGE (u)-[iv:INTERACTED_WITH]->(r)
SET iv.event_type = 'cook',
    iv.timestamp = timestamp,
    iv.rating = toFloat(4.0 + rand() * 1.0);

// 3. Tạo save interactions
MATCH (u:User {user_id: 'u_1'})
MATCH (r:Recipe) 
WHERE r.recipe_id IN ['rec_116', 'rec_143']
WITH u, r, datetime() - duration({days: toInteger(rand() * 30)}) AS timestamp
MERGE (u)-[iv:INTERACTED_WITH]->(r)
SET iv.event_type = 'save',
    iv.timestamp = timestamp;

// 4. Tạo view interactions
MATCH (u:User {user_id: 'u_1'})
MATCH (r:Recipe) 
WHERE r.recipe_id IN ['rec_3', 'rec_4', 'rec_5']
WITH u, r, datetime() - duration({days: toInteger(rand() * 30)}) AS timestamp
MERGE (u)-[iv:INTERACTED_WITH]->(r)
SET iv.event_type = 'view',
    iv.timestamp = timestamp;