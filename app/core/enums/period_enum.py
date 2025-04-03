from enum import Enum


class PeriodEnum(int, Enum):
    ONE_DAY = 1
    THREE_DAYS = 3
    FIVE_DAYS = 5
    TEN_DAYS = 10
    FIFTEEN_DAYS = 15
