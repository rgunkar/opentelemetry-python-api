"""
Database and cache tracing instrumentation module.
"""

import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Global state to track instrumented libraries
_instrumented_libraries = set()


def setup_database_tracing(
        databases: Optional[List[str]] = None,
        redis_enabled: bool = True,
        **kwargs: Any,
) -> None:
    """
    Set up database and cache tracing instrumentation.

    Args:
        databases: List of database types to instrument.
                  Supported: ['postgresql', 'mysql', 'sqlite', 'sqlalchemy', 'pymongo']
                  If None, will attempt to instrument all available databases.
        redis_enabled: Whether to enable Redis tracing.
        **kwargs: Additional configuration parameters for specific instrumentors.
    """
    if databases is None:
        databases = ['postgresql', 'mysql', 'sqlite', 'sqlalchemy', 'pymongo']

    logger.info(f"Setting up database tracing for: {databases}")

    # Instrument databases
    for db_type in databases:
        _instrument_database(db_type, **kwargs)

    # Instrument Redis if enabled
    if redis_enabled:
        _instrument_redis(**kwargs)


def _instrument_database(db_type: str, **kwargs: Any) -> None:
    """Instrument a specific database type."""
    if db_type in _instrumented_libraries:
        logger.debug(f"{db_type} already instrumented, skipping")
        return

    try:
        if db_type == 'postgresql':
            _instrument_postgresql(**kwargs)
        elif db_type == 'mysql':
            _instrument_mysql(**kwargs)
        elif db_type == 'sqlite':
            _instrument_sqlite(**kwargs)
        elif db_type == 'sqlalchemy':
            _instrument_sqlalchemy(**kwargs)
        elif db_type == 'pymongo':
            _instrument_pymongo(**kwargs)
        else:
            logger.warning(f"Unsupported database type: {db_type}")
            return

        _instrumented_libraries.add(db_type)
        logger.info(f"Successfully instrumented {db_type}")

    except ImportError as e:
        logger.warning(f"Failed to instrument {db_type}: {e}")
    except Exception as e:
        logger.error(f"Error instrumenting {db_type}: {e}")


def _instrument_postgresql(**kwargs: Any) -> None:
    """Instrument PostgreSQL via psycopg2."""
    try:
        from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

        if not Psycopg2Instrumentor().is_instrumented_by_opentelemetry:
            Psycopg2Instrumentor().instrument(**kwargs)

    except ImportError:
        logger.warning(
            "psycopg2 instrumentation not available. "
            "Install with: pip install opentelemetry-instrumentation-psycopg2"
        )


def _instrument_mysql(**kwargs: Any) -> None:
    """Instrument MySQL via PyMySQL."""
    try:
        from opentelemetry.instrumentation.pymysql import PyMySQLInstrumentor

        if not PyMySQLInstrumentor().is_instrumented_by_opentelemetry:
            PyMySQLInstrumentor().instrument(**kwargs)

    except ImportError:
        logger.warning(
            "PyMySQL instrumentation not available. "
            "Install with: pip install opentelemetry-instrumentation-pymysql"
        )


def _instrument_sqlite(**kwargs: Any) -> None:
    """Instrument SQLite."""
    try:
        from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor

        if not SQLite3Instrumentor().is_instrumented_by_opentelemetry:
            SQLite3Instrumentor().instrument(**kwargs)

    except ImportError:
        logger.warning(
            "SQLite3 instrumentation not available. "
            "Install with: pip install opentelemetry-instrumentation-sqlite3"
        )


def _instrument_sqlalchemy(**kwargs: Any) -> None:
    """Instrument SQLAlchemy ORM."""
    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        if not SQLAlchemyInstrumentor().is_instrumented_by_opentelemetry:
            SQLAlchemyInstrumentor().instrument(**kwargs)

    except ImportError:
        logger.warning(
            "SQLAlchemy instrumentation not available. "
            "Install with: pip install opentelemetry-instrumentation-sqlalchemy"
        )


def _instrument_pymongo(**kwargs: Any) -> None:
    """Instrument MongoDB via PyMongo."""
    try:
        from opentelemetry.instrumentation.pymongo import PymongoInstrumentor

        if not PymongoInstrumentor().is_instrumented_by_opentelemetry:
            PymongoInstrumentor().instrument(**kwargs)

    except ImportError:
        logger.warning(
            "PyMongo instrumentation not available. "
            "Install with: pip install opentelemetry-instrumentation-pymongo"
        )


def _instrument_redis(**kwargs: Any) -> None:
    """Instrument Redis."""
    if 'redis' in _instrumented_libraries:
        logger.debug("Redis already instrumented, skipping")
        return

    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        if not RedisInstrumentor().is_instrumented_by_opentelemetry:
            RedisInstrumentor().instrument(**kwargs)

        _instrumented_libraries.add('redis')
        logger.info("Successfully instrumented Redis")

    except ImportError:
        logger.warning(
            "Redis instrumentation not available. "
            "Install with: pip install opentelemetry-instrumentation-redis"
        )
    except Exception as e:
        logger.error(f"Error instrumenting Redis: {e}")


def setup_custom_database_tracing(
        connection_string: str,
        db_type: str,
        **kwargs: Any,
) -> None:
    """
    Set up tracing for custom database connections.

    Args:
        connection_string: Database connection string.
        db_type: Type of database (for labeling).
        **kwargs: Additional configuration.
    """
    # This is a placeholder for custom database instrumentation
    # You would implement specific logic based on your database driver
    logger.info(f"Setting up custom tracing for {db_type} database")

    # Example: You could create custom spans for database operations
    # This would require implementing custom instrumentation logic


def get_instrumented_libraries() -> List[str]:
    """Get list of currently instrumented libraries."""
    return list(_instrumented_libraries)


def reset_instrumentation() -> None:
    """Reset instrumentation state (mainly for testing)."""
    global _instrumented_libraries
    _instrumented_libraries = set()
