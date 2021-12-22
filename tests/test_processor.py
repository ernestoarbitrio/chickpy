import pytest

from chickpy.parser import parser
from chickpy.processor import _CreateChartProcessor


class Describe_CreateChartProcessor:
    @pytest.mark.parametrize(
        "script",
        (
            ("""CREATE CHART "pippo" XVALUES [-1,2,3,4] YVALUES [4,5,6,7];"""),
            ("""CREATE CHART "pippo" YVALUES [4,5,6,7]  XVALUES [-1,2,3,4];"""),
        ),
    )
    def it_validates_and_build_the_chart_data(self, script):
        tree = parser.parse(script)

        processor = _CreateChartProcessor(tree.children[0].children[0])
        processor.validate()

        assert processor._chart == {
            "label": '"pippo"',
            "xvalues": [-1.0, 2.0, 3.0, 4.0],
            "yvalues": [4.0, 5.0, 6.0, 7.0],
        }
