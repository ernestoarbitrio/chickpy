from functools import cached_property as lazy_property

import matplotlib.pyplot as plt  # type: ignore


class _BaseBackend:
    def __init__(self, chart: dict):
        self._chart = chart

    @lazy_property
    def _chart_type(self) -> str:
        return self._chart.get("options", {}).get("chart_type", "LINE")

    @lazy_property
    def _method_name(self) -> str:
        return {"SCATTER": "scatter", "LINE": "plot"}.get(self._chart_type, "plot")


class MatplotlibBackend(_BaseBackend):
    def render(self) -> None:
        plt.title(self._chart["label"].replace('"', ""))
        getattr(plt, self._method_name)(self._chart["xvalues"], self._chart["yvalues"])
        plt.show()
