from cliff.lister import Lister
from cliff.show import ShowOne

from common.codebook import (
        Codebook,
        CodebookManager,
        )


class ListCodebook(Lister):
    def take_action(self, args):
        codebook_manager = CodebookManager(".")

        return (
                ("Date", "Name", "Size"),
                [(cb.modification_date, cb.name, cb._size) for cb in sorted(codebook_manager.get_codebooks())]
                )


class ShowCodebook(ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowCodebook, self).get_parser(prog_name)
        parser.add_argument("cbname")
        return parser

    def take_action(self, args):
        codebook = Codebook.load_from_path(args.cbname)

        return (
                ("Name", "Date", "Size", "Stopword Ratio"),
                (
                    codebook.name,
                    codebook.modification_date,
                    codebook._size,
                    codebook._stopword_ratio
                    )
                )
