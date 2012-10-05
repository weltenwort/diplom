import common
import common.codebook

from manage_codebook import process_image


def get_signature(source_image_filename, data, codebook):
    import common.diskcache

    cache_config = data["config"].get("cache", {})
    if cache_config.get("signature_enabled", False):
        signature_cache = common.diskcache.SignatureDiskCache.from_config(data["config"])
    else:
        signature_cache = common.diskcache.NullCache()

    if signature_cache.contains(source_image_filename):
        signature = signature_cache.get(source_image_filename)
    else:
        config = data["config"]
        _, features = process_image(source_image_filename, data)
        signature = codebook.quantize(features,\
                use_stopwords=config["weights"]["use_stopwords"],
                use_weights=config["weights"]["use_weights"],
                )
        signature_cache.set(source_image_filename, signature)
    return source_image_filename, signature


@common.ApplicationBase.argument("-b", "--codebook", action="store", dest="codebook", default=None)
class CodebookFeaturesBenchmark(common.PRBenchmarkBase):
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

                for source_image_filename, signature in self.logger.sync_loop(
                        get_signature,
                        *common.augment_list(
                            common.glob_list(data["config"]["source_images"]),
                            data,
                            codebook,
                            ),
                        entry_message="Processing {count} images...",
                        item_prefix="image"):
                    self.logger.log("Processing image '{}'...".format(source_image_filename))

                    #self.logger.log(signature)
                    data["distances"][image_set["query_image"]][source_image_filename] =\
                            common.load(config["metric"]["metric"]).execute(query_signature, signature, data=data)
                self.logger.log("Calculating precisions for '{}'...".format(image_set["query_image"]))
                a = data["precisions"][image_set["query_image"]] = self.get_precision_recall(image_set["query_image"], data["distances"][image_set["query_image"]], study)
                self.logger.log("Precisions: {}".format(a))

        #correlations, mean_correlation = self.correlate_to_study(data["distances"], study)
        #precision_recall_stats, mean_stats = self.correlate_to_study(data["distances"], study)
        #self.logger.log("Mean correlation: {}".format(mean_correlation))
        return (data["precisions"], self.get_mean_average_precision(data["precisions"]))

if __name__ == "__main__":
    CodebookFeaturesBenchmark()()
