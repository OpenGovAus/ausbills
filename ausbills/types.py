from enum import Enum

# Parliaments

class Parliament(Enum):
    FEDERAL = "FEDERAL"
    NSW = "NSW"
    WA = "WA"
    NT = "NT"
    QLD = "QLD"
    VIC = "VIC"
    SA = "SA"
    TAS = "TAS"
    ACT = "ACT"


class House(Enum):
    UPPER = "UPPER"
    LOWER = "LOWER"

# Bills

class BillTypes(Enum):
    GOVERNMENT = 'GOVERNMENT'
    PRIVATE_MEMBER = 'PRIVATE_MEMBER'