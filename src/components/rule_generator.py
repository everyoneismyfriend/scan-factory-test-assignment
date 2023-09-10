from collections import defaultdict
from typing import Iterable

from .models import Domain, Rule
from .validator import DomainNameValidator, InvalidDomainName


class RuleGenerator:
    def __init__(self, validator: DomainNameValidator):
        self._validator = validator
        self._valid_domain_names: set[str] = set()
        self._invalid_domain_names: defaultdict[str, set[str]] = defaultdict(set)

    def make_rules(self, domains: Iterable[Domain]) -> list[Rule]:
        self._analyze_domains(domains)

        return [
            self._make_rule(project_id, domain_names)
            for project_id, domain_names in self._invalid_domain_names.items()
        ]

    def _analyze_domains(self, domains: Iterable[Domain]) -> None:
        for domain in domains:

            domain_level = 2
            while True:
                try:
                    domain_name = self._extract_domain_name(domain_level, domain.name)
                except AssertionError:
                    break

                if domain_name in self._valid_domain_names:
                    domain_level += 1
                    continue

                elif any(
                    domain_name in domain_names_group
                    for domain_names_group in self._invalid_domain_names.values()
                ):
                    break

                try:
                    self._validator.validate_domain_name(domain_name)
                except InvalidDomainName:
                    self._invalid_domain_names[domain.project_id].add(domain_name)
                    break
                else:
                    self._valid_domain_names.add(domain_name)
                    domain_level += 1

    @staticmethod
    def _extract_domain_name(domain_level: int, domain_name: str) -> str:
        components = domain_name.split('.')
        first_entry_idx = len(components) - domain_level
        assert first_entry_idx >= 0

        return '.'.join(components[first_entry_idx:])

    @staticmethod
    def _make_rule(project_id: str, domain_names: set[str]) -> Rule:
        escaped_domain_names = (
            domain_name.replace('.', '\.')
            for domain_name in domain_names
        )
        regexp = '.*(' + '|'.join(escaped_domain_names) + ')$'

        return Rule(project_id, regexp)