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


class BillProgress(Enum):
    FIRST = 'FIRST'
    SECOND = 'SECOND'
    ASSENTED = 'ASSENTED'

# There are three stages for a bill to pass a chamber in any state/territory,
# where the bill's short title is read in parliament (readings).
# https://www.aph.gov.au/About_Parliament/House_of_Representatives/Powers_practice_and_procedure/Practice7/HTML/Chapter10/Bills%E2%80%94the_parliamentary_process


class ChamberProgress(Enum):
    FIRST_READING = 1
    SECOND_READING = 2
    THIRD_READING = 3  # I assume it's fine to not start this at 0, since we're not calling any indexes with it.
