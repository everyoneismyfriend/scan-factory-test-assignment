from abc import ABC, abstractmethod

from dns.resolver import Resolver, NXDOMAIN, NoAnswer


class InvalidDomainName(Exception):
    pass


class DomainNameValidator(ABC):
    @abstractmethod
    def validate_domain_name(self, domain_name: str) -> None:
        """
        raises: InvalidDomainName
        """


class WildCardDomainNameValidator(DomainNameValidator):
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
        except (NXDOMAIN, NoAnswer):
            return set()
        return set(answers.addresses())

    @staticmethod
    def _build_wildcard_domain_name(domain_name: str) -> str:
        return '.'.join(['*', *domain_name.split('.')[1:]])
