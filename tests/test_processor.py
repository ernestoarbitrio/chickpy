import csv

import pytest
from lark.exceptions import UnexpectedToken
from matplotlib.figure import Figure
from mock import patch

import chickpy.backend as backend  # noqa
from chickpy.backend import MatplotlibBackend
from chickpy.enums import CHART_TYPE
from chickpy.parser import parser
from chickpy.processor import Command, _CommandProcessor, _CreateChartProcessor

from .util import class_mock, instance_mock


class Describe_CreateChartProcessor:
    @pytest.mark.parametrize(
        "script, expected_value",
        (
            (
                """CREATE CHART "foo" XVALUES [-1,2,3,4] YVALUES [4,5,6,7];""",
                {
                    "label": '"foo"',
                    "xvalues": [-1.0, 2.0, 3.0, 4.0],
                    "yvalues": [4.0, 5.0, 6.0, 7.0],
                    "options": {},
                },
            ),
            (
                """CREATE CHART "foo" YVALUES [4,5,6,7] XVALUES [-1,2,3,4];""",
                {
                    "label": '"foo"',
                    "xvalues": [-1.0, 2.0, 3.0, 4.0],
                    "yvalues": [4.0, 5.0, 6.0, 7.0],
                    "options": {},
                },
            ),
            (
                """CREATE CHART "foo" VALUES [-1,2,3,4] [4,5,6,7];""",
                {
                    "label": '"foo"',
                    "xvalues": [-1.0, 2.0, 3.0, 4.0],
                    "yvalues": [4.0, 5.0, 6.0, 7.0],
                    "options": {},
                },
            ),
            (
                """CREATE CHART "foo" VALUES [-1,2,3,4] [4,5,6,7] TYPE LINE;""",
                {
                    "label": '"foo"',
                    "xvalues": [-1.0, 2.0, 3.0, 4.0],
                    "yvalues": [4.0, 5.0, 6.0, 7.0],
                    "options": {"chart_type": CHART_TYPE.LINE},
                },
            ),
            (
                """CREATE CHART "foo" VALUES [-1,2,3,4] [4,5,6,7] TYPE SCATTER;""",
                {
                    "label": '"foo"',
                    "xvalues": [-1.0, 2.0, 3.0, 4.0],
                    "yvalues": [4.0, 5.0, 6.0, 7.0],
                    "options": {"chart_type": CHART_TYPE.SCATTER},
                },
            ),
            (
                """CREATE CHART "foo" XVALUES ["a", "b"] YVALUES [4,5] TYPE BAR;""",
                {
                    "label": '"foo"',
                    "xvalues": ["a", "b"],
                    "yvalues": [4.0, 5.0],
                    "options": {"chart_type": CHART_TYPE.BAR},
                },
            ),
        ),
    )
    def it_validates_and_build_the_chart_data(self, script, expected_value):
        tree = parser.parse(script)
        backend_ = MatplotlibBackend
        processor = _CreateChartProcessor(tree.children[0].children[0], backend_)
        processor.validate()

        assert processor._chart == expected_value

    @pytest.mark.parametrize(
        "script, csv_file",
        (
            (
                """CREATE CHART "foo" FROM CSV placeholder;""",
                '"tests/fixtures/csv/base_csv_comma_separated.csv"',
            ),
            (
                """CREATE CHART "foo" FROM CSV placeholder;""",
                '"tests/fixtures/csv/base_csv_semicolon_separated.csv"',
            ),
        ),
    )
    def it_validates_and_build_the_chart_data_from_csv(self, script, csv_file):
        tree = parser.parse(script.replace("placeholder", csv_file))
        backend_ = MatplotlibBackend
        processor = _CreateChartProcessor(tree.children[0].children[0], backend_)
        processor.validate()

        assert processor._chart == {
            "label": '"foo"',
            "xvalues": [0.0, 1.0, 2.0, 4.0, 8.0],
            "yvalues": [1.0, 2.0, 3.0, 7.0, 9.0],
            "options": {},
        }

    def but_it_raises_an_exception_when_ther_is_a_delimiter_mismatch(self):
        script = """CREATE CHART "foo" FROM CSV "tests/fixtures/csv/base_csv_wrong_sep.csv";"""  # noqa
        tree = parser.parse(script)
        backend_ = MatplotlibBackend
        processor = _CreateChartProcessor(tree.children[0].children[0], backend_)
        with pytest.raises(csv.Error) as e:
            processor.validate()

        assert (
            str(e.value) == "Could not determine delimiter. Allowed delimiters are ,;|~"
        )

    def but_it_raises_an_error_if_the_command_is_wrong(self):
        script = "CREATE foo;"
        with pytest.raises(UnexpectedToken) as e:
            parser.parse(script)

        assert (
            str(e.value)
            == "Unexpected token Token('IDENTIFIER', 'foo') at line 1, column "
            "8.\nExpected one of: \n\t* CHART\nPrevious tokens: [Token('_WS', ' ')]\n"
        )

    def and_it_raises_another_error_when_the_chart_type_is_wrong(self):
        script = """CREATE CHART "foo" VALUES [-1,2,3,4] [4,5,6,7] TYPE FOO;"""
        with pytest.raises(UnexpectedToken) as e:
            parser.parse(script)

        expected_error_message = (
            "Unexpected token Token('IDENTIFIER', 'FOO') at line"
            " 1, column 53.\nExpected one of: \n\t* CHART_TYPE\n\t* _SEMICOLON\n\t* "
            "_WS\nPrevious tokens: [Token('_WS', ' ')]\n"
        )
        diff = set(expected_error_message.splitlines()) ^ set(str(e.value).splitlines())

        assert not diff

    @pytest.mark.parametrize("chart_type", ("BAR", "HORIZONTAL BAR"))
    def and_it_raises_value_error_when_the_chart_type_and_xvals_are_incompatible(
        self, chart_type
    ):
        script = (
            f"""CREATE CHART "foo" XVALUES [1,2] YVALUES [4,5,6,7] TYPE {chart_type};"""
        )
        tree = parser.parse(script)
        backend_ = MatplotlibBackend
        processor = _CreateChartProcessor(tree.children[0].children[0], backend_)

        with pytest.raises(ValueError) as e:
            processor.validate()

        assert str(e.value) == f"{chart_type} cannot have numeric x values."

    @pytest.mark.parametrize(
        "script, expected_chart_data",
        (
            (
                """CREATE CHART "foo" FROM CSV "{}" FOR x BY y;""",
                {
                    "label": '"foo"',
                    "xvalues": [0.0, 1.0, 2.0, 4.0, 8.0],
                    "yvalues": [1.0, 2.0, 3.0, 7.0, 9.0],
                    "options": {},
                },
            ),
            (
                """CREATE CHART "foo" FROM CSV "{}" FOR x BY z;""",
                {
                    "label": '"foo"',
                    "xvalues": [0.0, 1.0, 2.0, 4.0, 8.0],
                    "yvalues": [1.0, 1.0, 2.0, 1.0, 2.0],
                    "options": {},
                },
            ),
            (
                """CREATE CHART "foo" FROM CSV "{}" FOR z BY y;""",
                {
                    "label": '"foo"',
                    "xvalues": [1.0, 1.0, 2.0, 1.0, 2.0],
                    "yvalues": [1.0, 2.0, 3.0, 7.0, 9.0],
                    "options": {},
                },
            ),
        ),
    )
    def it_builds_chart_data_from_csv_for_specific_columnss(
        self, script, expected_chart_data
    ):
        filename = "tests/fixtures/csv/multi_column.csv"
        tree = parser.parse(script.format(filename))
        backend_ = MatplotlibBackend
        processor = _CreateChartProcessor(tree.children[0].children[0], backend_)
        processor.validate()

        assert processor._chart == expected_chart_data

    @pytest.mark.parametrize(
        "script, expected_error_msg",
        (
            (
                """CREATE CHART "chart" FROM CSV "{}" FOR foo BY bar;""",
                "Unknown column `foo` specified",
            ),
            (
                """CREATE CHART "chart" FROM CSV "{}" FOR x BY bar;""",
                "Unknown column `bar` specified",
            ),
        ),
    )
    def but_it_fails_on_unknown_column_names(self, script, expected_error_msg):
        filename = "tests/fixtures/csv/multi_column.csv"
        tree = parser.parse(script.format(filename))
        backend_ = MatplotlibBackend
        processor = _CreateChartProcessor(tree.children[0].children[0], backend_)
        with pytest.raises(ValueError) as err:
            processor.validate()

        assert err.value.args[0] == expected_error_msg


class Describe_CommandProcessor:
    def it_provides_a_factory_for_constructing_processor_objects(self, request):
        script = """CREATE CHART "foo" VALUES [-1,2,3,4] [4,5,6,7] TYPE LINE;"""
        tree = parser.parse(script)
        processor_ = instance_mock(request, _CreateChartProcessor)
        _CreateChartProcessorCls = class_mock(
            request,
            "chickpy.processor._CreateChartProcessor",
            return_value=processor_,
        )
        with patch(
            "chickpy.processor.PROCESSORS", {"create_chart": _CreateChartProcessorCls}
        ):
            processor = _CommandProcessor.factory(tree)

        assert processor is processor_
        _CreateChartProcessorCls.assert_called_once_with(
            tree.children[0].children[0], MatplotlibBackend
        )


class Describe_Command:
    @patch("%s.backend.plt" % __name__)
    @pytest.mark.parametrize(
        "script",
        (
            ("""CREATE CHART "foo" VALUES [-1,2,3,4] [4,5,6,7] TYPE LINE;"""),
            ("""CREATE CHART "foo" VALUES [-1,2,3,4] [4,5,6,7];"""),
            ("""CREATE CHART "foo" XVALUES [-1,2,3,4] YVALUES [4,5,6,7] TYPE LINE;"""),
            ("""CREATE CHART "foo" XVALUES [-1,2,3,4] YVALUES [4,5,6,7];"""),
        ),
    )
    def it_parses_and_plot_a_line_chart(self, mock_plt, script):
        Command.run(script, show_output=False)

        assert mock_plt.figure.called
        assert mock_plt.plot.called
        mock_plt.title.assert_called_once_with("foo")
        mock_plt.plot.assert_called_once_with(
            [-1.0, 2.0, 3.0, 4.0], [4.0, 5.0, 6.0, 7.0]
        )

    @patch("%s.backend.plt" % __name__)
    @pytest.mark.parametrize(
        "script",
        (
            ("""CREATE CHART "foo" VALUES [-1,2,3] [4,5,6] TYPE SCATTER;"""),
            ("""CREATE CHART "foo" XVALUES [-1,2,3] YVALUES [4,5,6] TYPE SCATTER;"""),
        ),
    )
    def it_parses_and_plot_a_scatter_chart(self, mock_plt, script):
        Command.run(script, show_output=False)

        assert mock_plt.figure.called
        assert mock_plt.scatter.called
        mock_plt.title.assert_called_once_with("foo")
        mock_plt.scatter.assert_called_once_with([-1.0, 2.0, 3.0], [4.0, 5.0, 6.0])

    @patch("%s.backend.plt" % __name__)
    @pytest.mark.parametrize(
        "script",
        (
            ("""CREATE CHART "foo" XVALUES ["a", "b"] YVALUES [4,5] TYPE BAR;"""),
            ("""CREATE CHART "foo" YVALUES [4,5] XVALUES ["a", "b"] TYPE BAR;"""),
        ),
    )
    def it_parses_and_plot_a_bar_chart(self, mock_plt, script):
        Command.run(script, show_output=False)

        assert mock_plt.figure.called
        assert mock_plt.bar.called
        mock_plt.title.assert_called_once_with("foo")
        mock_plt.bar.assert_called_once_with(["a", "b"], [4.0, 5.0])

    @patch("%s.backend.plt" % __name__)
    @pytest.mark.parametrize(
        "script",
        (
            ("""CREATE CHART "foo" XVALUES ["a"] YVALUES [4] TYPE HORIZONTAL BAR;"""),
            ("""CREATE CHART "foo" YVALUES [4] XVALUES ["a"] TYPE HORIZONTAL BAR;"""),
        ),
    )
    def it_parses_and_plot_a_horizondal_bar_chart(self, mock_plt, script):
        Command.run(script, show_output=False)

        assert mock_plt.figure.called
        assert mock_plt.barh.called
        mock_plt.title.assert_called_once_with("foo")
        mock_plt.barh.assert_called_once_with(["a"], [4.0])

    @patch("%s.backend.plt" % __name__)
    @pytest.mark.parametrize(
        "script, plot_type",
        (
            ("""CREATE CHART "foo" FROM CSV csv_placeholder TYPE LINE;""", "plot"),
            ("""CREATE CHART "foo" FROM CSV csv_placeholder;""", "plot"),
            (
                """CREATE CHART "foo" FROM CSV csv_placeholder TYPE SCATTER;""",
                "scatter",
            ),
        ),
    )
    def it_parses_and_plot_chart_from_csv(self, mock_plt, script, plot_type):
        script = script.replace(
            "csv_placeholder", '"tests/fixtures/csv/base_csv_comma_separated.csv"'
        )
        Command.run(script, show_output=False)

        assert mock_plt.figure.called
        assert getattr(mock_plt, plot_type).called
        mock_plt.title.assert_called_once_with("foo")
        getattr(mock_plt, plot_type).assert_called_once_with(
            [0.0, 1.0, 2.0, 4.0, 8.0], [1.0, 2.0, 3.0, 7.0, 9.0]
        )

    def it_returns_a_figure_object_using_the_render_method(self):
        script = """CREATE CHART "foo" VALUES [1,2,3] [4,5,6] TYPE LINE;"""
        fig = Command.render(script)

        assert isinstance(fig, Figure)
