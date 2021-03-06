import common
import common.codebook

from manage_codebook import process_image


#def process_image(source_image_filename, data):
    #import common
    #import common.diskcache

    #if data["config"].get("cache", {}).get("enabled", False):
        #feature_cache = common.diskcache.DiskCache.from_dict_key(dict(
            #readers=data["config"]["readers"],
            #curvelets=data["config"]["curvelets"],
            #features=dict((k, v) for k, v in data["config"]["features"].items() if k in ["extractor", "grid_size", "patch_size"]),
            #), prefix=data["config"].get("cache", {}).get("cache_prefix", "cache_features_"))
    #else:
        #feature_cache = common.diskcache.NullCache()

    #if feature_cache.contains(source_image_filename):
        #features = feature_cache.get(source_image_filename)
    #else:
        #image = common.load(data["config"]["readers"]["image"]).execute(source_image_filename, data=data)
        #coefficients = common.load(data["config"]["curvelets"]["transform"]).execute(image, data=data)
        #features = common.load(data["config"]["features"]["extractor"]).execute(coefficients, data=data)
        #feature_cache.set(source_image_filename, features)
    #return source_image_filename, features


@common.ApplicationBase.argument("-b", "--codebook", action="store", dest="codebook", default=None)
class CodebookFeaturesBenchmark(common.BenchmarkBase):
    @common.BenchmarkBase.subcommand()
    def execute(self, args, config, study):
        if args.codebook is not None:
            codebook = common.codebook.Codebook.load_from_path(args.codebook, size=config["codebook"]["codebook_size"])
        else:
            codebook = common.codebook.Codebook.load_from_config(config)

        data = common.RDict(config=config)
        data["codewords"] = codebook.codewords
        for image_set in self.logger.loop(
                data["config"]["images"],
                entry_message="Processing {count} image sets",
                item_prefix="image set"):
            if image_set.get("skip_benchmark", False):
                self.logger.log("Skipping distractor image set...")
            else:
                self.logger.log("Processing query image '{}'...".format(image_set["query_image"]))

                query_image = common.load(config["readers"]["query"]).execute(image_set["query_image"], data=data)
                query_coefficients = common.load(config["curvelets"]["transform"]).execute(query_image, data=data)
                query_features = common.load(config["features"]["extractor"]).execute(query_coefficients, data=data)
                query_signature = codebook.quantize(query_features,
                        use_stopwords=config["weights"]["use_stopwords"],
                        use_weights=config["weights"]["use_weights"],
                        )
                #self.logger.log(query_signature)

                for source_image_filename, features in self.logger.sync_loop(
                        process_image,
                        *common.augment_list(
                            common.glob_list(image_set["source_images"]),
                            data,
                            ),
                        entry_message="Processing {count} images...",
                        item_prefix="image"):
                    self.logger.log("Processing image '{}'...".format(source_image_filename))

                    signature = codebook.quantize(features,\
                            use_stopwords=config["weights"]["use_stopwords"],
                            use_weights=config["weights"]["use_weights"],
                            )
                    #self.logger.log(signature)
                    a = data["distances"][image_set["query_image"]][source_image_filename] =\
                            common.load(config["metric"]["metric"]).execute(query_signature, signature, data=data)
                    self.logger.log("Distance: {}".format(a))

        correlations, mean_correlation = self.correlate_to_study(data["distances"], study)
        #self.logger.log("Mean correlation: {}".format(mean_correlation))
        return (correlations, mean_correlation)

if __name__ == "__main__":
    CodebookFeaturesBenchmark()()
