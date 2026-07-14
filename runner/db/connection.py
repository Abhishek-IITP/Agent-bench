"""Database connection management."""

from typing import Any, Optional

import psycopg2
from psycopg2 import pool

from runner.logging import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """Manages PostgreSQL connections with connection pooling."""

    _instance = None
    _pool = None

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "agentbench",
        user: str = "postgres",
        password: str = "postgres",
        min_connections: int = 1,
        max_connections: int = 10,
    ):
        """
        Initialize database connection manager.

        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            database: Database name
            user: Database user
            password: Database password
            min_connections: Minimum pool connections
            max_connections: Maximum pool connections
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

        try:
            if DatabaseConnection._pool is None:
                DatabaseConnection._pool = pool.SimpleConnectionPool(
                    min_connections,
                    max_connections,
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password,
                )
                logger.info(
                    "Database connection pool created",
                    host=host,
                    database=database,
                    pool_size=f"{min_connections}-{max_connections}",
                )
        except psycopg2.DatabaseError as e:
            logger.error("Failed to create connection pool", error=str(e))
            raise

    @staticmethod
    def get_instance(
        host: str = "localhost",
        port: int = 5432,
        database: str = "agentbench",
        user: str = "postgres",
        password: str = "postgres",
    ) -> "DatabaseConnection":
        """Get singleton instance."""
        if DatabaseConnection._instance is None:
            DatabaseConnection._instance = DatabaseConnection(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
            )
        return DatabaseConnection._instance

    def get_connection(self):
        """Get a connection from the pool."""
        if DatabaseConnection._pool is None:
            raise RuntimeError("Connection pool not initialized")

        return DatabaseConnection._pool.getconn()

    def put_connection(self, conn) -> None:
        """Return a connection to the pool."""
        if DatabaseConnection._pool is not None:
            DatabaseConnection._pool.putconn(conn)

    def execute(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch: bool = False,
    ) -> Any:
        """
        Execute a query.

        Args:
            query: SQL query
            params: Query parameters
            fetch: Whether to fetch results

        Returns:
            Query results if fetch=True, otherwise number of rows affected
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(query, params or ())

            if fetch:
                results = cursor.fetchall()
                conn.commit()
                return results
            else:
                rows_affected = cursor.rowcount
                conn.commit()
                return rows_affected

        except psycopg2.DatabaseError as e:
            if conn:
                conn.rollback()
            logger.error("Database query error", error=str(e), query=query[:100])
            raise

        finally:
            if conn:
                self.put_connection(conn)

    def execute_many(
        self,
        query: str,
        params_list: list[tuple],
    ) -> int:
        """
        Execute multiple queries.

        Args:
            query: SQL query
            params_list: List of parameter tuples

        Returns:
            Total rows affected
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            total_rows = 0
            for params in params_list:
                cursor.execute(query, params)
                total_rows += cursor.rowcount

            conn.commit()
            return total_rows

        except psycopg2.DatabaseError as e:
            if conn:
                conn.rollback()
            logger.error("Database batch error", error=str(e))
            raise

        finally:
            if conn:
                self.put_connection(conn)

    def close_all(self) -> None:
        """Close all connections in pool."""
        if DatabaseConnection._pool:
            DatabaseConnection._pool.closeall()
            DatabaseConnection._pool = None
            logger.info("Database connection pool closed")
