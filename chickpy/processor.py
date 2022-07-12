from functools import cached_property as lazy_property
from typing import Any, List, Type, Union

from lark import Token, Tree

from chickpy.backend import Figure, MatplotlibBackend
from chickpy.datasource import DataSource
from chickpy.enums import CHART_TYPE
from chickpy.options import ChartOptions
from chickpy.parser import parser


class Command:
    """
    Object representing a base command.

    Attributes
    ----------
    script : str
        A string representing the a Graph Definition Languate command.

    Methods
    -------
    run(script: str, show_output: bool = True)
        Parse validate and run the given script. If show_output is False the output will
        be hidden. Default is True.

    Usage
    -----
    >>> from chickpy.processor import Command
    >>> Command.run(\"""CREATE CHART "foo" VALUES [-1,2,3,4] [4,5,6,7] TYPE LINE;\""")
    """

    def __init__(self, script: str):
        self._script = script

    @classmethod
    def run(cls, script: str, show_output: bool = True) -> None:
        tree: Tree = parser.parse(script)
        processor: _CreateChartProcessor = _CommandProcessor.factory(tree)
        processor.validate()
        processor.backend.render(show_output)

    @classmethod
    def render(cls, script: str) -> Figure:
        tree: Tree = parser.parse(script)
        processor: _CreateChartProcessor = _CommandProcessor.factory(tree)
        processor.validate()
        return processor.backend.figure()


class _CreateChartProcessor:
    """Processes the Tree node from the script corresponding to create_chart."""

    _chart: dict = {}

    def __init__(self, tree: Tree, backend: Type[MatplotlibBackend]):
        self._tree = tree
        self._backend = backend

    @lazy_property
    def backend(self) -> MatplotlibBackend:
        return self._backend(self._chart)

    def validate(self) -> None:
        label: Token = self._pick_node("label", self._tree.children)[0]
        data_source_tree: Union[str, Tree] = self._tree.children[1]
        chart_options_nodes: List = self._pick_nodes(
            "chart_options", self._tree.children
        )
        xvalues, yvalues = DataSource.values(data_source_tree)
        options: dict = ChartOptions.values(chart_options_nodes)
        self._validate(xvalues, options)
        self._chart = {
            "label": label.value,
            "xvalues": xvalues,
            "yvalues": yvalues,
            "options": options,
        }

    def _pick_nodes(self, node_type: str, nodes: list) -> List:
        """In a list of nodes, return all nodes matching the type."""
        matches: List = [
            n for n in nodes if isinstance(n, Tree) and n.data == node_type
        ]
        return [m.children for m in matches]

    def _pick_node(self, node_type: str, nodes: list) -> List:
        """In a list of nodes, return the first node matching the type.

        Use this when you have optional nodes in a Tree's children.
        """
        matches: List[Tree] = [
            n for n in nodes if isinstance(n, Tree) and n.data == node_type
        ]
        return matches[0].children if matches else [Token("", "")]  # type: ignore

    def _validate(self, xvalues: List[Union[str, float]], options: dict) -> None:
        chart_type: CHART_TYPE = options.get("chart_type", CHART_TYPE.LINE)
        if chart_type in CHART_TYPE.BARS() and all(
            isinstance(x, float) for x in xvalues
        ):
            raise ValueError(
                f"{chart_type.name.replace('_', ' ')} cannot have numeric x values."
            )


class _CommandProcessor:
    def __init__(self, tree: Tree):
        self._tree = tree

    @classmethod
    def factory(cls, tree: Tree) -> _CreateChartProcessor:
        return cls(tree)._factory()

    def _factory(self) -> _CreateChartProcessor:
        command_node: Tree = self._command_node(self._tree.children[0])
        command_token: Any = command_node.data
        backend: Type[MatplotlibBackend] = MatplotlibBackend
        ChartProcessorCls: Type[_CreateChartProcessor] = PROCESSORS.get(
            command_token.value, _CreateChartProcessor
        )
        return ChartProcessorCls(command_node, backend)

    def _command_node(self, node) -> Tree:
        if isinstance(node, Tree):
            if isinstance(node.children[0], Tree):
                return node.children[0]
        raise TypeError("Node type mismatch")


PROCESSORS = {"create_chart": _CreateChartProcessor}
