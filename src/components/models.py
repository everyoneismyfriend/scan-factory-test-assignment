from dataclasses import dataclass


@dataclass
class Domain:
    project_id: str
    name: str


@dataclass
class Rule:
    project_id: str
    regexp: str
