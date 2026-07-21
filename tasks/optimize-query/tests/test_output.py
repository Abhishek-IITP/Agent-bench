#!/usr/bin/env python3
"""Test harness for optimize-query task."""

from pathlib import Path
import sys


def test_optimized_query_exists():
    """Test that optimized_query.sql exists."""
    query_file = Path('optimized_query.sql')
    assert query_file.exists(), "optimized_query.sql not found"


def test_optimized_query_readable():
    """Test that query file is readable."""
    try:
        with open('optimized_query.sql', 'r') as f:
            content = f.read()
        assert len(content) > 0, "Query file is empty"
    except Exception as e:
        raise AssertionError(f"Failed to read query file: {e}")


def test_query_is_sql():
    """Test that file contains SQL syntax."""
    with open('optimized_query.sql', 'r') as f:
        content = f.read().upper()
    
    assert 'SELECT' in content, "Query should contain SELECT"
    assert 'FROM' in content, "Query should contain FROM"


def test_query_uses_specific_columns():
    """Test that query doesn't use SELECT *."""
    with open('optimized_query.sql', 'r') as f:
        content = f.read()
    
    # Extract SELECT clause
    lines = content.split('\n')
    select_clause = ' '.join([l for l in lines if l.strip() and not l.strip().startswith('--')])
    
    # Check for SELECT * (bad) vs specific columns (good)
    # Allow SELECT * in comments but not in actual query
    if 'SELECT *' in select_clause and '-- SELECT *' not in select_clause:
        # Check if it's really in the active query
        active_query = '\n'.join([l for l in lines if not l.strip().startswith('--')])
        if 'SELECT *' in active_query:
            raise AssertionError("Query should specify columns instead of using SELECT *")


def test_query_avoids_correlated_subquery():
    """Test that query doesn't use inefficient subquery pattern."""
    with open('optimized_query.sql', 'r') as f:
        content = f.read()
    
    # Check for improvement from subquery pattern
    # The original has: WHERE id IN (SELECT user_id FROM orders ...)
    # Better approach: JOIN
    
    lines = content.split('\n')
    active_lines = [l for l in lines if l.strip() and not l.strip().startswith('--')]
    active_query = '\n'.join(active_lines).upper()
    
    # If it uses JOIN, it's better than subquery
    has_join = 'JOIN' in active_query
    has_subquery = 'IN (SELECT' in active_query or 'EXISTS (SELECT' in active_query
    
    # Prefer JOIN over subquery
    assert has_join or not has_subquery, \
        "Query should use JOIN instead of subquery for better performance"


def test_query_has_where_clause():
    """Test that query has WHERE clause for filtering."""
    with open('optimized_query.sql', 'r') as f:
        content = f.read().upper()
    
    assert 'WHERE' in content, "Query should have WHERE clause for filtering"


def test_query_has_comments():
    """Test that query includes optimization comments."""
    with open('optimized_query.sql', 'r') as f:
        content = f.read()
    
    # Should have comments explaining optimizations
    lines = content.split('\n')
    comments = [l for l in lines if l.strip().startswith('--')]
    
    assert len(comments) > 0, "Query should include comments explaining optimizations"


if __name__ == '__main__':
    try:
        test_optimized_query_exists()
        test_optimized_query_readable()
        test_query_is_sql()
        test_query_uses_specific_columns()
        test_query_avoids_correlated_subquery()
        test_query_has_where_clause()
        test_query_has_comments()
        print("All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
