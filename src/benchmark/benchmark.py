import logging
import sys

from cliff.app import App
from cliff.interactive import InteractiveApp
#from cliff.command import Command
from cliff.commandmanager import CommandManager

from clicommands.configs import (
        ListConfigs,
        ShowConfig,
        )
from clicommands.results import (
        CollectResults,
        PlotPrResults
        )


class BenchmarkApp(App):
    log = logging.getLogger(__name__)

    def __init__(self):
        command_manager = CommandManager("diplom.benchmark")
        command_manager.add_command("config show", ShowConfig)
        command_manager.add_command("config list", ListConfigs)
        command_manager.add_command("results collect", CollectResults)
        command_manager.add_command("results plotpr", PlotPrResults)
        #command_manager.add_command("codebook show", ShowCodebook)
        super(BenchmarkApp, self).__init__(
                description="Benchmark management application",
                version="0.1",
                command_manager=command_manager,
                interactive_app_factory=InteractiveBenchmarkApp,
                )


class InteractiveBenchmarkApp(InteractiveApp):
    def completenames(self, text, *ignored):
        return InteractiveApp.completenames(self, text) + [n for n in self.command_manager.commands.keys() if n.startswith(text)]


if __name__ == "__main__":
    app = BenchmarkApp()
    sys.exit(app.run(sys.argv[1:]))
