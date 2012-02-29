import sys

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from pathlib import Path

from loader import load_results


class ComparisonTable(Directive):
    required_arguments = 1
    final_argument_whitespace = False
    has_content = False

    def run(self):
        results_path = Path(str(directives.path(self.arguments[0])))
        if not results_path.is_absolute():
            source = str(self.state_machine.input_lines.source(
                    self.lineno - self.state_machine.input_offset - 1))
            results_path = Path(source).resolve().parent().join(results_path)
        results = load_results(results_path)

        #return [self.create_table([["a", "b"], ]), ]
        return []

    def create_table(self, data):
        table_node = nodes.table()

        if len(data) > 0:
            tgroup_node = nodes.tgroup(cols=len(data[0]))
            table_node += tgroup_node

            col_width = 100 // len(data[0])
            for col_index in range(len(data)):
                colspec_node = nodes.colspec(colwidth=col_width)
                tgroup_node += colspec_node

            tbody = nodes.tbody()
            tgroup_node += tbody
            for row in data:
                row_node = nodes.row()
                for cell in row:
                    cell_node = nodes.entry()
                    cell_node += nodes.Text(unicode(cell))
                    row_node += cell_node
                tbody += row_node

        return table_node


def setup(app):
    app.add_directive('comparisontable', ComparisonTable)
