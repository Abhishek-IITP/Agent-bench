# Optimize Database Query

## Objective
Analyze an inefficient SQL query and provide an optimized version that achieves the same result with better performance.

## Input
A file named `inefficient_query.sql` containing a slow SQL query.

## Task
1. Review the inefficient query
2. Identify performance issues:
   - Missing or improper indexes
   - Unnecessary subqueries
   - Inefficient JOINs
   - Full table scans
   - Redundant conditions
   - Poor query structure
3. Write an optimized version to `optimized_query.sql`
4. The optimized query must:
   - Return exactly the same results
   - Use proper indexing strategy
   - Minimize table scans
   - Use efficient JOIN types
   - Avoid unnecessary operations

## Example Inefficiency Issues
- Using SELECT * instead of specific columns
- Subqueries instead of joins
- Multiple nested loops
- Missing WHERE clause conditions that could filter early
- Sorting before filtering
- Joining unindexed columns
- Using LIKE with leading wildcard
- Multiple passes over same data

## Output Format
The `optimized_query.sql` file should contain:
1. Comment explaining the optimizations made
2. The optimized SQL query

Example:
```sql
-- Optimizations made:
-- 1. Added index on user_id column
-- 2. Replaced subquery with JOIN
-- 3. Moved expensive calculations to WHERE clause

SELECT u.id, u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2020-01-01'
GROUP BY u.id, u.name
ORDER BY order_count DESC;
```

## Common Optimization Techniques
- Add indexes on frequently filtered/joined columns
- Replace subqueries with JOINs
- Use efficient WHERE clause conditions
- SELECT only needed columns
- Use EXPLAIN to analyze query plan
- Partition large tables
- Use materialized views
- Batch operations
- Use proper JOIN types (INNER vs LEFT)
