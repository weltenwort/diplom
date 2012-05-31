# flake8: noqa
import glob

import common
import common.codebook


@common.ApplicationBase.argument("-b", "--codebook", action="store",\
        dest="codebook", required=True)
class CodebookFeaturesBenchmark(common.BenchmarkBase):
    @common.BenchmarkBase.subcommand()
    def execute(self, args, config, study):
        codebook = common.codebook.Codebook(args.codebook,\
                config["features"]["codebook_size"])
        codebook.load()

        data = common.RDict(config=common.RDict.from_dict(config))
        for image_set in self.logger.loop(
                data["config"]["images"],
                entry_message="Processing {count} image sets",
                item_prefix="image set"):
            self.logger.log("Processing query image '{}'...".format(image_set["query_image"]))

            query_image = common.load(data["config"]["readers"]["query"]).execute(image_set["query_image"], data=data)
            query_coefficients = common.load(data["config"]["curvelets"]["transform"]).execute(query_image, data=data)
            query_features = common.load(data["config"]["features"]["extractor"]).execute(query_coefficients, data=data)
            query_signature = codebook.quantize(query_features)
            #self.logger.log(query_signature)

            for source_image_filename in self.logger.loop(
                    common.glob_list(image_set["source_images"]),
                    entry_message="Processing {count} images...",
                    item_prefix="image"):
                self.logger.log("Processing image '{}'...".format(source_image_filename))

                image = common.load(data["config"]["readers"]["image"]).execute(source_image_filename, data=data)
                coefficients = common.load(data["config"]["curvelets"]["transform"]).execute(image, data=data)
                features = common.load(data["config"]["features"]["extractor"]).execute(coefficients, data=data)
                signature = codebook.quantize(features)
                #self.logger.log(signature)
                a = data["distances"][image_set["query_image"]][source_image_filename] = common.load(data["config"]["metric"]["metric"]).execute(query_signature, signature, data=data)

        correlations, mean_correlation = self.correlate_to_study(data["distances"], study)
        self.logger.log("Mean correlation: {}".format(mean_correlation))
        return (correlations, mean_correlation)

if __name__ == "__main__":
    CodebookFeaturesBenchmark()()
