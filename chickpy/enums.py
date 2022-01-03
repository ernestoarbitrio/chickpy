from enum import Enum


class CHART_TYPE(Enum):
    LINE = "plot"
    SCATTER = "scatter"
    BAR = "bar"
    HORIZONTAL_BAR = "barh"

    @classmethod
    def BARS(cls):
        return [cls.BAR, cls.HORIZONTAL_BAR]
