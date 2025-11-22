from ..db import get_session

def update_user_profile_incremental(user_id: str):
    """
    Re-calculate user's TF-IDF profile (user_terms, user_weights)
    based on their interactions (like, rating, view).
    This runs in the background to keep the profile up-to-date.
    """
    q = """
    MATCH (u:User {user_id: $uid})-[iv:INTERACTED_WITH]->(r:Recipe)
    WHERE r.text_terms IS NOT NULL AND r.text_weights IS NOT NULL
          AND size(r.text_terms) = size(r.text_weights)
    WITH u, iv, r
    WITH u, r,
         CASE iv.event_type 
            WHEN 'like' THEN 1.0 
            WHEN 'rating' THEN 0.8 
            WHEN 'view' THEN 0.2 
            ELSE 0.1 
         END AS w,
         // Use updated_at if available, else created_at
         coalesce(iv.updated_at, iv.created_at, datetime()) AS interaction_time
    
    // Time decay: events older than 90 days have half weight
    WITH u, w, duration.between(interaction_time, datetime()).days AS daysAgo, r
    WITH u, w * exp(-log(2) * toFloat(daysAgo) / 90.0) AS weight, r

    // Aggregate weighted terms
    WITH u, weight, r, range(0, size(r.text_terms)-1) AS idxs
    UNWIND idxs AS k
    WITH u, r.text_terms[k] AS term, (weight * coalesce(r.text_weights[k],0.0)) AS contrib
    WITH u, term, sum(contrib) AS val
    
    // Build final vectors
    WITH u, collect([term, val]) AS vec
    WITH u, vec,
         [x IN vec | x[0]] AS terms,
         [x IN vec | x[1]] AS weights
    
    // Update user node
    SET u.user_terms = terms, u.user_weights = weights
    """
    
    try:
        with get_session() as s:
            s.run(q, uid=user_id)
            # print(f"✅ Updated user profile for {user_id} (incremental)")
    except Exception as e:
        print(f"❌ Failed to update user profile for {user_id}: {e}")

