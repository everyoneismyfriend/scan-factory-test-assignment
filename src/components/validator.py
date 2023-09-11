from abc import ABC, abstractmethod

from dns.resolver import Resolver, NXDOMAIN, NoAnswer, LifetimeTimeout, NoNameservers
from validators.domain import domain


class InvalidDomainName(Exception):
    pass


class DomainNameValidator(ABC):
    """
    Abstract class for domain name validators
    """
    @abstractmethod
    def validate_domain_name(self, domain_name: str) -> None:
        """ Raises InvalidDomainName """


class RegEXDomainNameValidator(DomainNameValidator):
    """
    Validate domain name format using validators package:
    https://python-validators.github.io/validators/reference/domain/
    """
    def validate_domain_name(self, domain_name: str) -> None:
        if not domain(domain_name):
            raise InvalidDomainName('Invalid domain format')


class WildCardDomainNameValidator(DomainNameValidator):
    """
    Check if given domain is resolved into the same IP address as a
    wildcard-domain of the same level, e.g. `*.example.com`
    """
    def __init__(self):
        self._resolver: Resolver = Resolver()
        self._resolver.lifetime = self._resolver.timeout = 5
        self._wildcard_names: dict[str, set[str]] = {}

    def validate_domain_name(self, domain_name: str) -> None:
        addresses = self._resolve_domain_name(domain_name)
        if not addresses:
            raise InvalidDomainName('Domain name does not exist')

        wildcard_domain_name = self._build_wildcard_domain_name(domain_name)
        wildcard_addresses = self._wildcard_names.get(wildcard_domain_name)
        if wildcard_addresses is None:
            wildcard_addresses = self._resolve_domain_name(wildcard_domain_name)
            self._wildcard_names[wildcard_domain_name] = wildcard_addresses

        if wildcard_addresses.intersection(addresses):
            raise InvalidDomainName('Wildcard domain name detected')

    def _resolve_domain_name(self, domain_name: str) -> set[str]:
        try:
            answers = self._resolver.resolve_name(domain_name)
        except (NXDOMAIN, NoAnswer, LifetimeTimeout, NoNameservers):
            return set()
        return set(answers.addresses())

    @staticmethod
    def _build_wildcard_domain_name(domain_name: str) -> str:
        return '.'.join(['*', *domain_name.split('.')[1:]])
