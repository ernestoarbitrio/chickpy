import matplotlib.pyplot as plt
from lark import Tree

from chickpy.parser import parser


class Command:
    def __init__(self, script):
        self._script = script

    @classmethod
    def run(cls, script):
        tree = parser.parse(script)
        processor = _CommandProcessor.factory(tree.children[0].children[0])
        processor.validate()
        processor.command().execute()


class _CommandProcessor:
    def __init__(self, tree):
        self._tree = tree

    @classmethod
    def factory(cls, tree):
        command_name = tree.data.value
        ChartProcessorCls = PROCESSORS.get(command_name)
        return ChartProcessorCls(tree)


class _DataSourceProcessor:
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


class _CreateChartProcessor:
    """Processes the Tree node from the script corresponding to create_chart."""

    def __init__(self, tree):
        self._tree = tree
        self._chart = {}

    def command(self):
        return _CreateChartCommand(self._chart)

    def validate(self):
        label = self.pick_node("label", self._tree.children)[0].value
        data_source_tree = self._tree.children[1]
        xvalues, yvalues = _DataSourceProcessor.values(data_source_tree)
        self._chart = {"label": label, "xvalues": xvalues, "yvalues": yvalues}

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


class _CreateChartCommand:
    def __init__(self, chart):
        self._chart = chart

    def execute(self):
        _, ax = plt.subplots()  # Create a figure containing a single axes.
        plt.title(self._chart["label"].replace('"', ""))
        ax.plot(self._chart["xvalues"], self._chart["yvalues"])
        plt.show()


PROCESSORS = {"create_chart": _CreateChartProcessor}
