from pathlib import Path

from lark import Lark


def read_language(filename: str) -> str:
    filepath: Path = Path(__file__).with_name(filename)
    return open(filepath).read()


def gen_parser() -> Lark:
    lang_def: str = read_language("language.lark")
    lang_parser: Lark = Lark(
        lang_def,
        keep_all_tokens=False,
        start="start",
        parser="lalr",
        lexer="contextual",
    )

    return lang_parser


parser: Lark = gen_parser()
