from pathlib import Path

from lark import Lark


def read_language(filename):
    filepath = Path(__file__).with_name(filename)
    return open(filepath).read()


def gen_parser():
    lang_def = read_language("language.lark")
    lark_kwargs = {
        "parser": "lalr",
        "lexer": "contextual",
    }
    lang_parser = Lark(lang_def, start="start", **lark_kwargs)

    return lang_parser


parser = gen_parser()
