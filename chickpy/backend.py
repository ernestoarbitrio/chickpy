from functools import cached_property as lazy_property

import matplotlib.pyplot as plt  # type: ignore

from chickpy.enums import CHART_TYPE


class _BaseBackend:
    def __init__(self, chart: dict):
        self._chart = chart

    @lazy_property
    def _chart_type(self) -> CHART_TYPE:
        return self._chart.get("options", {}).get("chart_type", CHART_TYPE.LINE)

    @lazy_property
    def _method_name(self) -> str:
        return self._chart_type.value


class MatplotlibBackend(_BaseBackend):
    def render(self, show: bool = True) -> None:
        plt.figure()  # Create a figure containing a single axes.
        plt.title(self._chart["label"][1:-1])
        getattr(plt, self._method_name)(self._chart["xvalues"], self._chart["yvalues"])
        if show:
            plt.show()
