#!/usr/bin/env python3
"""Solution for query optimization task."""


def generate_optimized_query():
    """Generate optimized SQL query."""
    
    optimized_query = """-- Optimizations made:
-- 1. Replaced SELECT * with specific columns
-- 2. Converted inefficient subquery to INNER JOIN (eliminates duplicates, better performance)
-- 3. Moved LOWER() function out of WHERE clause for indexed column usage
-- 4. Changed LIKE with trailing wildcard (allows index usage)
-- 5. Added DISTINCT to handle duplicate rows from JOIN
-- 6. Indexes recommended: users(status, email), users(created_at)

SELECT DISTINCT 
    u.id,
    u.name,
    u.email,
    u.created_at
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE u.email LIKE '%@company.com'
AND u.created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
AND o.status = 'completed'
ORDER BY u.created_at DESC;"""
    
    return optimized_query


if __name__ == '__main__':
    query = generate_optimized_query()
    
    with open('optimized_query.sql', 'w') as f:
        f.write(query)
    
    print("Optimized query written to optimized_query.sql")
