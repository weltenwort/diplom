import json
import re

import common
import common.codebook


def process_image(source_image_filename, data):
    import common
    import common.diskcache

    if data["config"].get("cache", {}).get("enabled", False):
        feature_cache = common.diskcache.DiskCache.from_dict_key(dict(
            readers=data["config"]["readers"],
            curvelets=data["config"]["curvelets"],
            features=dict((k, v) for k, v in data["config"]["features"].items() if k in ["extractor", "grid_size", "patch_size"]),
            ), prefix=data["config"].get("cache", {}).get("cache_prefix", "cache_features_"))
    else:
        feature_cache = common.diskcache.NullCache()

    if feature_cache.contains(source_image_filename):
        features = feature_cache.get(source_image_filename)
    else:
        image = common.load(data["config"]["readers"]["image"]).execute(source_image_filename, data=data)
        coefficients = common.load(data["config"]["curvelets"]["transform"]).execute(image, data=data)
        features = common.load(data["config"]["features"]["extractor"]).execute(coefficients, data=data)
        feature_cache.set(source_image_filename, features)

    return source_image_filename, features


@common.ApplicationBase.argument("-b", "--codebook", action="store", dest="codebook", required=True)
class CodebookManager(common.ApplicationBase):
    DEFAULT_COMMAND = "create"

    @common.ApplicationBase.subcommand(help="create a new codebook")
    def create(self, args, config):
        codebook = common.codebook.Codebook(args.codebook, config["features"]["codebook_size"])

        data = common.RDict(config=common.RDict.from_dict(config))
        for image_set in self.logger.loop(
                data["config"]["images"],
                entry_message="Processing {count} image sets",
                item_prefix="image set"):
            for source_image_filename, features in self.logger.sync_loop(
                    process_image,
                    *common.augment_list(
                        common.glob_list(image_set["source_images"]),
                        data,
                        ),
                    entry_message="Processing {count} images...",
                    item_prefix="image"):
                self.logger.log("Processing image '{}'...".format(source_image_filename))
                codebook.add_observations(features)
        self.logger.log("Clustering observations...")
        codebook.cluster()
        self.logger.log("Saving codebook...")
        codebook.save()

    @common.ApplicationBase.subcommand(help="preprocess images")
    @common.ApplicationBase.argument("-k", "--key", action="store", dest="key", default=None)
    def preprocess(self, args, config):
        data = common.RDict(config=common.RDict.from_dict(config))
        if args.key is not None:
            key_expression = re.compile(args.key)
            image_sets = [image_set for image_set in data["config"]["images"] if key_expression.search(image_set["key"]) is not None]
        else:
            image_sets = data["config"]["images"]
        for image_set in self.logger.loop(
                image_sets,
                entry_message="Processing {count} image sets",
                item_prefix="image set"):
            for source_image_filename, features in self.logger.sync_loop(
                    process_image,
                    *common.augment_list(
                        common.glob_list(image_set["source_images"]),
                        data,
                        ),
                    entry_message="Processing {count} images...",
                    item_prefix="image"):
                self.logger.log("Processing image '{}'...".format(source_image_filename))

    @common.ApplicationBase.subcommand(\
            help="print information about a codebook")
    def info(self, args, config):
        codebook = common.codebook.Codebook.from_cache(args.codebook)

        info = {
                "cluster_count": codebook._k,
                "stopword_ratio": codebook._stopword_ratio,
                "stopword_indices": list(codebook.stopwords),
                "frequencies": list(codebook.frequencies),
                }
        print(json.dumps(info, indent=4))


if __name__ == "__main__":
    CodebookManager()()
