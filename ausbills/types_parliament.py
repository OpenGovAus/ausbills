from enum import Enum


class Parliament(Enum):
    FEDERAL = "FEDERAL"
    NSW = "NSW"
    WA = "WA"
    NT = "NT"
    QLD = "QLD"
    VIC = "VIC"
    SA = "SA"
    TAS = "TAS"


class House(Enum):
    UPPER = "UPPER"
    LOWER = "LOWER"
