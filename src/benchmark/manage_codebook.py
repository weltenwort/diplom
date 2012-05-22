import common


@common.ApplicationBase.argument("-b", "--codebook", action="store",\
        dest="codebook", required=True)
class CodebookManager(common.ApplicationBase):
    DEFAULT_COMMAND = "create"

    @common.ApplicationBase.subcommand(help="create a new codebook")
    def create(self, args, config):
        codebook = common.DiskCache(args.codebook)

        data = common.RDict(config=common.RDict.from_dict(config))
        for image_set in self.logger.loop(
                data["config"]["images"],
                entry_message="Processing {count} image sets",
                item_prefix="image set"):
            pass


if __name__ == "__main__":
    CodebookManager()()
