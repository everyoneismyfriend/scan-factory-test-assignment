import logging
import sqlite3
import sys
from contextlib import closing

from components import SQLiteService, WildCardDomainNameValidator, RuleGenerator

DB_PATH = 'domains.db'


def configure_logging() -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format='[%(asctime)s] - %(name)s - %(message)s',
    )


def main():
    configure_logging()

    with closing(sqlite3.connect(DB_PATH)) as db_connection:
        db_service = SQLiteService(connection=db_connection)
        domains = db_service.retrieve_domains()

        domain_name_validator = WildCardDomainNameValidator()
        rule_generator = RuleGenerator(validator=domain_name_validator)
        rules = rule_generator.make_rules(domains)

        db_service.create_rules(rules)


if __name__ == '__main__':
    main()
