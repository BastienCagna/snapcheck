from dataclasses import dataclass


@dataclass
class CATIProtocol:
    protocol: str

@dataclass
class CATIStudy(CATIProtocol):
    study: str

@dataclass
class CATICenter(CATIStudy):
    center: str

@dataclass
class CATISubject(CATICenter):
    subject: str

@dataclass
class CATIVisit(CATISubject):
    visit: str
