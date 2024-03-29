import csv
from abc import ABC, abstractproperty
from dataclasses import dataclass
from functools import cached_property as lazy_property
from pathlib import Path
from typing import Any, List, Tuple, Union

DELIMITERS = ",;|~"


class DataSource(ABC):
    def sanitize_value(self, value: str) -> Union[str, float]:
        try:
            return float(value)
        except ValueError:
            return value[1:-1]

    @classmethod
    def values(cls, data_src_tree: Any) -> Tuple[List[Union[str, float]], List[float]]:
        data_source: str = data_src_tree.children[0].data.value
        if data_source == "data_source_csv":
            return _DataSourceCsv(data_src_tree).data
        return _DataSourceStd(data_src_tree).data

    @abstractproperty
    def data(self) -> Tuple[List[Union[str, float]], List[float]]:
        pass


@dataclass
class _DataSourceCsv(DataSource):
    _data_source_tree: Any

    @lazy_property
    def data(self) -> Tuple[List[Union[str, float]], List[float]]:
        with open(self._file_path, mode="r") as csv_file:
            try:
                dialect = csv.Sniffer().sniff(csv_file.read(), delimiters=DELIMITERS)
            except csv.Error as e:
                raise csv.Error(f"{str(e)}. Allowed delimiters are {DELIMITERS}")
            csv_file.seek(0)
            csv_reader = csv.DictReader(
                csv_file,
                quoting=csv.QUOTE_MINIMAL,
                dialect=dialect,
            )
            values: List[dict] = list(csv_reader)
        xvalues = [self.sanitize_value(row["x"]) for row in values]
        yvalues = [float(row["y"]) for row in values]
        return xvalues, yvalues

    @property
    def _file_path(self) -> Path:
        file: str = self._data_source_tree.children[0].children[0].value[1:-1]
        return Path(file).resolve()


@dataclass
class _DataSourceStd(DataSource):
    _data_source_tree: Any

    @lazy_property
    def data(self) -> Tuple[List[Union[str, float]], List[float]]:
        xvalues: map = map(
            lambda x: self.sanitize_value(x.children[0].value),
            list(self._data_source_tree.find_data("x_values"))[0].children,
        )
        yvalues: map = map(
            lambda x: float(x.children[0].value),
            list(self._data_source_tree.find_data("y_values"))[0].children,
        )
        return list(xvalues), list(yvalues)
