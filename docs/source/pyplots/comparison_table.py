#import sys

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList
from pathlib import Path
#from sphinx.util.nodes import nested_parse_with

from loader import load_results


class ComparisonTable(Directive):
    required_arguments = 1
    final_argument_whitespace = False
    has_content = False
    option_spec = {
            "feature_template": directives.unchanged,
            "metric_template": directives.unchanged,
            }

    FEATURE_PARAMETERS_TEMPLATE = """.. code-block:: javascript

    {content}"""

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

        headers = ["Label", "Angles", "Scales", "Input", "Features", "Metric",\
                "Feature Parameters", "Mean Correlation"]
        data = [self.extract_result(r) for r in results]

        return [self.create_table([headers, ] + data), ]
        #return []

    def extract_result(self, result):
        parameters = result.get("parameters", {})
        return [
                result["label"],
                parameters.get("angles", 0),
                parameters.get("scales", 0),
                parameters.get("image_reader"),
                parameters.get("feature_extractor", ""),
                parameters.get("metric", ""),
                parameters.get("feature_parameters", ""),
                result["mean_correlation"],
                ]

    def create_cell(self, col_index, cell_item, is_header=False):
        feature_template = self.options.get("feature_template",\
                ":doc:`{target}`")
        metric_template = self.options.get("metric_template",\
                ":doc:`{target}`")

        cell_node = nodes.entry()
        block = None
        if not is_header and cell_item:
            if col_index == 4:
                block = StringList(feature_template.format(target=cell_item)\
                        .splitlines())
            elif col_index == 5:
                block = StringList(metric_template.format(target=cell_item)\
                        .splitlines())
            #elif col_index == 5:
                #block = StringList(self.FEATURE_PARAMETERS_TEMPLATE\
                        #.format(content=cell_item).splitlines())

        if block:
            self.state.nested_parse(block, 0, cell_node)
        else:
            text_node = nodes.Text(unicode(cell_item))
            paragraph_node = nodes.paragraph(unicode(cell_item), '',\
                    text_node)
            cell_node += paragraph_node
        return cell_node

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
                for col_index, cell_item in enumerate(row):
                    row_node += self.create_cell(col_index, cell_item,\
                            row_index < num_headers)
                if row_index < num_headers:
                    thead += row_node
                else:
                    tbody += row_node

        return table_node


def setup(app):
    app.add_directive('comparisontable', ComparisonTable)
