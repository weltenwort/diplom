import common
import common.codebook


@common.ApplicationBase.argument("-b", "--codebook", action="store",\
        dest="codebook", required=True)
class CodebookManager(common.ApplicationBase):
    DEFAULT_COMMAND = "create"

    @common.ApplicationBase.subcommand(help="create a new codebook")
    def create(self, args, config):
        codebook = common.codebook.Codebook(args.codebook,\
                config["features"]["codebook_size"])

        data = common.RDict(config=common.RDict.from_dict(config))
        for image_set in self.logger.loop(
                data["config"]["images"],
                entry_message="Processing {count} image sets",
                item_prefix="image set"):
            for source_image_filename in self.logger.loop(
                    common.glob_list(image_set["source_images"]),
                    entry_message="Processing {count} images...",
                    item_prefix="image"):
                self.logger.log("Processing image '{}'...".\
                        format(source_image_filename))
                image = common.load(data["config"]["readers"]["image"]).execute(source_image_filename, data=data)
                coefficients = common.load(data["config"]["curvelets"]["transform"]).execute(image, data=data)
                features = common.load(data["config"]["features"]["extractor"]).execute(coefficients, data=data)
                codebook.add_observations(features)
        self.logger.log("Clustering observations...")
        codebook.cluster()
        self.logger.log("Saving codebook...")
        codebook.save()


if __name__ == "__main__":
    CodebookManager()()
