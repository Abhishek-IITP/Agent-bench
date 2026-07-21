-- Inefficient query: Multiple issues with performance
-- Issues:
-- 1. Uses SELECT * (unnecessary columns)
-- 2. Has redundant subquery
-- 3. Inefficient use of functions in WHERE clause
-- 4. No indexes on filtered columns
-- 5. LIKE with leading wildcard prevents index usage

SELECT *
FROM users u
WHERE id IN (
    SELECT user_id 
    FROM orders o
    WHERE LOWER(o.status) = 'completed'
)
AND LOWER(u.email) LIKE '%@company.com'
AND u.created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY u.created_at DESC;
