from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property as lazy_property

import matplotlib.pyplot as plt  # type: ignore
from matplotlib.figure import Figure  # type: ignore

from chickpy.enums import CHART_TYPE


class Backend(ABC):
    _chart: dict

    @abstractmethod
    def render(self, show: bool = True) -> None:
        pass

    @abstractmethod
    def figure(self) -> Figure:
        pass

    @lazy_property
    def _method_name(self) -> str:
        chart_type = self._chart.get("options", {}).get("chart_type", CHART_TYPE.LINE)
        return chart_type.value


@dataclass
class MatplotlibBackend(Backend):
    _chart: dict

    def render(self, show: bool = True) -> None:
        plt.figure()  # Create a figure containing a single axes.
        plt.title(self._chart["label"][1:-1])
        getattr(plt, self._method_name)(self._chart["xvalues"], self._chart["yvalues"])
        if show:
            plt.show()

    def figure(self) -> Figure:
        fig, ax = plt.subplots()
        getattr(ax, self._method_name)(self._chart["xvalues"], self._chart["yvalues"])
        ax.set_title(self._chart["label"][1:-1])
        return fig
