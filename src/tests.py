import unittest
from unittest.mock import patch, Mock

import dns

from components.models import Domain
from components.rule_generator import RuleGenerator
from components.validator import (
    RegEXDomainNameValidator,
    WildCardDomainNameValidator,
    InvalidDomainName,
)


def mock_answers(name):
    def addresses():
        if name == 'random.example.com':
            return ['0.0.0.1', '0.0.0.2']
        elif name == '*.example.com':
            return ['0.0.0.2', '0.0.0.3']
        elif name in ('example.com', 'valid.example.com'):
            return ['0.0.0.1']

    if name in ('*.com', 'nonexistent.com'):
        raise dns.resolver.NXDOMAIN

    answers = Mock()
    answers.addresses = addresses

    return answers


class TestRegEXDomainNameValidator(unittest.TestCase):
    def test_nonexistent_domain_name_validation(self):
        domain_name = 'invalid?syntax.com'

        domain_name_validator = RegEXDomainNameValidator()
        with self.assertRaises(InvalidDomainName):
            domain_name_validator.validate_domain_name(domain_name)


@patch.object(dns.resolver.Resolver, 'resolve_name', side_effect=mock_answers)
class TestWildCardDomainNameValidator(unittest.TestCase):
    def test_nonexistent_domain_name_validation(self, mock_resolver):
        domain_name = 'nonexistent.com'

        domain_name_validator = WildCardDomainNameValidator()
        with self.assertRaises(InvalidDomainName):
            domain_name_validator.validate_domain_name(domain_name)

    def test_wildcard_domain_name_validation(self, mock_resolver):
        domain_name = 'random.example.com'

        domain_name_validator = WildCardDomainNameValidator()
        with self.assertRaises(InvalidDomainName):
            domain_name_validator.validate_domain_name(domain_name)


@patch.object(dns.resolver.Resolver, 'resolve_name', side_effect=mock_answers)
class TestRuleGenerator(unittest.TestCase):
    def test_invalid_syntax_domain_name_validation(self, mock_resolver):
        domains = [
            Domain('1', 'invalid?syntax.com'),
            Domain('1', 'valid.example.com'),
            Domain('1', 'nonexistent.com'),
            Domain('1', 'random.example.com'),
        ]

        domain_name_validator = WildCardDomainNameValidator()
        rule_generator = RuleGenerator(validators=[domain_name_validator])
        rule, *_ = rule_generator.make_rules(domains)

        # Since rules are constructed from sets, the order of invalid domains
        # is not preserved
        expected_regex = {
            r'.*(invalid?syntax\.com|nonexistent\.com|random\.example\.com)$',
            r'.*(invalid?syntax\.com|random\.example\.com|nonexistent\.com)$',
            r'.*(nonexistent\.com|invalid?syntax\.com|random\.example\.com)$',
            r'.*(nonexistent\.com|random\.example\.com|invalid?syntax\.com)$',
            r'.*(random\.example\.com|invalid?syntax\.com|nonexistent\.com)$',
            r'.*(random\.example\.com|nonexistent\.com|invalid?syntax\.com)$',
        }
        self.assertIn(rule.regexp, expected_regex)
