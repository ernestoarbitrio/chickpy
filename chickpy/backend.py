from functools import cached_property as lazy_property

import matplotlib.pyplot as plt


class _BaseBackend:
    def __init__(self, chart):
        self._chart = chart

    @lazy_property
    def _chart_type(self):
        return self._chart.get("options", {}).get("chart_type", "LINE")

    @lazy_property
    def _method_name(self):
        return {"SCATTER": "scatter", "LINE": "plot"}.get(self._chart_type, "plot")


class MatplotlibBackend(_BaseBackend):
    def render(self):
        plt.title(self._chart["label"].replace('"', ""))
        getattr(plt, self._method_name)(self._chart["xvalues"], self._chart["yvalues"])
        plt.show()
