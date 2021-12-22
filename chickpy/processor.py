from functools import cached_property as lazy_property

from lark import Tree

from chickpy.backend import MatplotlibBackend
from chickpy.parser import parser


class Command:
    def __init__(self, script):
        self._script = script

    @classmethod
    def run(cls, script):
        tree = parser.parse(script)
        processor = _CommandProcessor.factory(tree.children[0].children[0])
        processor.validate()
        processor.backend.render()


class _CommandProcessor:
    def __init__(self, tree):
        self._tree = tree

    @classmethod
    def factory(cls, tree):
        command_name = tree.data.value
        backend = MatplotlibBackend
        ChartProcessorCls = PROCESSORS.get(command_name)
        return ChartProcessorCls(tree, backend)


class _CreateChartProcessor:
    """Processes the Tree node from the script corresponding to create_chart."""

    def __init__(self, tree, backend):
        self._tree = tree
        self._backend = backend
        self._chart = {}

    @lazy_property
    def backend(self):
        return self._backend(self._chart)

    def validate(self):
        label = self.pick_node("label", self._tree.children)[0].value
        data_source_tree = self._tree.children[1]
        chart_options_nodes = self.pick_nodes("chart_options", self._tree.children)
        xvalues, yvalues = _DataSource.values(data_source_tree)
        options = _ChartOptions.values(chart_options_nodes)
        self._chart = {
            "label": label,
            "xvalues": xvalues,
            "yvalues": yvalues,
            "options": options,
        }

    def pick_nodes(self, node_type, nodes):
        """In a list of nodes, return all nodes matching the type."""
        matches = [n for n in nodes if isinstance(n, Tree) and n.data == node_type]
        return [m.children for m in matches]

    def pick_node(self, node_type, nodes, default=None):
        """In a list of nodes, return the first node matching the type.

        Use this when you have optional nodes in a Tree's children.
        """
        default = [] if default is None else default
        if not nodes:
            return default
        matches = [n for n in nodes if isinstance(n, Tree) and n.data == node_type]
        return matches[0].children if matches else default


# ==================================NODE PARSERS========================================


class _ChartOptions:
    def __init__(self, options_nodes):
        self._options_nodes = options_nodes

    @classmethod
    def values(cls, options_nodes):
        options = dict()
        for node in options_nodes:
            for token in node:
                options[token.type.lower()] = token.value
        return options


class _DataSource:
    def __init__(self, data_source_tree):
        self._data_source_tree = data_source_tree

    @classmethod
    def values(cls, data_source_tree):
        xvalues = map(
            lambda x: float(x.children[0].value),
            list(data_source_tree.find_data("x_values"))[0].children,
        )
        yvalues = map(
            lambda x: float(x.children[0].value),
            list(data_source_tree.find_data("y_values"))[0].children,
        )
        return list(xvalues), list(yvalues)


# ======================================================================================


PROCESSORS = {"create_chart": _CreateChartProcessor}
