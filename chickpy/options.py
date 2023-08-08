from dataclasses import dataclass
from typing import List

from chickpy.enums import CHART_TYPE


@dataclass
class ChartOptions:
    _options_nodes: List[list]

    @classmethod
    def values(cls, options_nodes: List[list]) -> dict:
        options: dict = dict()
        for node in options_nodes:
            for token in node:
                options[token.type.lower()] = getattr(
                    CHART_TYPE, token.value.replace(" ", "_")
                )
        return options
