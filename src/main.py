import argparse
import logging
import os
import sqlite3
import sys
from contextlib import contextmanager
from typing import ContextManager

from components import SQLiteService, WildCardDomainNameValidator, RuleGenerator

logger = logging.getLogger(__name__)


@contextmanager
def acquire_sqlite_connection(db_path: str) -> ContextManager[sqlite3.Connection]:
    if not os.path.isfile(db_path):
        logger.error(f'SQLite database file not found: {db_path}')
        exit(1)

    connection = sqlite3.connect(db_path)
    try:
        yield connection
    finally:
        connection.close()


def configure_logging() -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('db_path', help='Path to the database file')
    return parser.parse_args()


def main():
    configure_logging()
    args = parse_args()

    with acquire_sqlite_connection(args.db_path) as db_connection:
        db_service = SQLiteService(connection=db_connection)
        domains = db_service.retrieve_domains()

        domain_name_validator = WildCardDomainNameValidator()
        rule_generator = RuleGenerator(validators=[domain_name_validator])
        rules = rule_generator.make_rules(domains)

        db_service.create_rules(rules)


if __name__ == '__main__':
    main()
