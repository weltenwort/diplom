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
        for result in results:
            self.state.document.settings.record_dependencies.add(str(
                result["path"]))

        headers = ["Label", "Angles", "Scales", "Features", "Metric",\
                "Feature Parameters", "Mean Correlation"]
        data = [self.create_row(r) for r in results]

        return [self.create_table([headers, ] + data), ]
        #return []

    def create_row(self, result):
        parameters = result.get("parameters", {})
        return [
                result["label"],
                parameters.get("angles", 0),
                parameters.get("scales", 0),
                parameters.get("feature_extractor", ""),
                parameters.get("metric", ""),
                parameters.get("feature_parameters", ""),
                result["mean_correlation"],
                ]

    def create_table(self, data, num_headers=1):
        table_node = nodes.table()

        if len(data) > 0:
            tgroup_node = nodes.tgroup(cols=len(data[0]))
            table_node += tgroup_node

            col_width = 100 // len(data[0])
            for col_index in range(len(data[0])):
                colspec_node = nodes.colspec(colwidth=col_width)
                tgroup_node += colspec_node

            thead = nodes.thead()
            tgroup_node += thead
            tbody = nodes.tbody()
            tgroup_node += tbody
            for row_index, row in enumerate(data):
                row_node = nodes.row()
                for cell in row:
                    cell_node = nodes.entry()
                    if isinstance(cell, nodes.Node):
                        cell_node += cell
                    else:
                        text_node = nodes.Text(unicode(cell))
                        paragraph_node = nodes.paragraph(unicode(cell), '',\
                                text_node)
                        cell_node += paragraph_node
                    row_node += cell_node
                if row_index < num_headers:
                    thead += row_node
                else:
                    tbody += row_node

        return table_node


def setup(app):
    app.add_directive('comparisontable', ComparisonTable)
