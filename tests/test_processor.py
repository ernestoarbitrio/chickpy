import pytest
from lark.exceptions import UnexpectedToken
from mock import patch

from chickpy.backend import MatplotlibBackend
from chickpy.parser import parser
from chickpy.processor import _CommandProcessor, _CreateChartProcessor

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
                """CREATE CHART "foo" YVALUES [4,5,6,7]  XVALUES [-1,2,3,4];""",
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
                    "options": {"chart_type": "LINE"},
                },
            ),
            (
                """CREATE CHART "foo" VALUES [-1,2,3,4] [4,5,6,7] TYPE SCATTER;""",
                {
                    "label": '"foo"',
                    "xvalues": [-1.0, 2.0, 3.0, 4.0],
                    "yvalues": [4.0, 5.0, 6.0, 7.0],
                    "options": {"chart_type": "SCATTER"},
                },
            ),
        ),
    )
    def it_validates_and_build_the_chart_data(self, script, expected_value):
        tree = parser.parse(script)
        backend = MatplotlibBackend
        processor = _CreateChartProcessor(tree.children[0].children[0], backend)
        processor.validate()

        assert processor._chart == expected_value

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
        _CreateChartProcessorCls.assert_called_once_with(tree, MatplotlibBackend)
