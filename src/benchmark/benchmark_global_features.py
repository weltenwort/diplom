# flake8: noqa
import glob

import common
import common.diskcache
from manage_codebook import process_image


class GlobalFeaturesBenchmark(common.BenchmarkBase):
    @common.BenchmarkBase.subcommand()
    def execute(self, args, config, study):
        #feature_cache = common.diskcache.DiskCache("cache_{}".format(common.dict_to_filename(config, ["images", ])))
        data = common.RDict(config=config)
        for image_set in self.logger.loop(
                data["config"]["images"],
                entry_message="Processing {count} image sets",
                item_prefix="image set"):
            self.logger.log("Processing query image '{}'...".format(image_set["query_image"]))

            query_image = common.load(config["readers"]["query"]).execute(image_set["query_image"], data=data)
            query_coefficients = common.load(config["curvelets"]["transform"]).execute(query_image, data=data)
            #data["images"][image_set_key]["query_features"] =\
            query_features = common.load(config["features"]["extractor"]).execute(query_coefficients, data=data)

            for source_image_filename, features in self.logger.sync_loop(
                    process_image,
                    *common.augment_list(
                        common.glob_list(image_set["source_images"]),
                        data,
                        ),
                    entry_message="Processing {count} images...",
                    item_prefix="image"):
                self.logger.log("Processing image '{}'...".format(source_image_filename))

                #if not feature_cache.contains(source_image_filename):
                    #image = common.load(data["config"]["readers"]["image"]).execute(source_image_filename, data=data)
                    #coefficients = common.load(data["config"]["curvelets"]["transform"]).execute(image, data=data)
                    ##data["images"][image_set_key]["source_images"][source_image_filename]["image_features"] =\
                    #features = common.load(data["config"]["features"]["extractor"]).execute(coefficients, data=data)
                    #feature_cache.set(source_image_filename, features)
                #else:
                    #features = feature_cache.get(source_image_filename)
                data["distances"][image_set["query_image"]][source_image_filename] =\
                        common.load(config["metric"]["metric"]).execute(query_features, features, data=data)
        correlations, mean_correlation = self.correlate_to_study(data["distances"], study)
        #self.logger.log("Mean correlation: {}".format(mean_correlation))
        return (correlations, mean_correlation)

if __name__ == "__main__":
    GlobalFeaturesBenchmark()()
