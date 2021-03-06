import json

from cliff.lister import Lister
from cliff.show import ShowOne
import pathlib

#from common.codebook import (
        #Codebook,
        #)
from common.diskcache import (
        CodebookDiskCache,
        FeatureDiskCache,
        ReaderDiskCache,
        )


class ListConfigs(Lister):
    def get_parser(self, prog_name):
        parser = super(ListConfigs, self).get_parser(prog_name)
        #parser.add_argument("-d", "--caches-directory", dest="caches_directory", default=[".", ], action="append")
        parser.add_argument("-p", "--config-pattern", dest="config_pattern", default="configs/*.config.json")
        return parser

    @staticmethod
    def _load_cache(cache_class, config):
        try:
            cache = cache_class.from_config(config)
        except IOError as e:
            print e
            return None
        else:
            if cache.exists():
                return cache
            else:
                None

    def take_action(self, args):
        config_filenames = pathlib.Path(".").glob(args.config_pattern)

        configs = {}
        for config_filename in config_filenames:
            with config_filename.open() as fp:
                config = json.load(fp)

            ccache = self._load_cache(CodebookDiskCache, config)
            fcache = self._load_cache(FeatureDiskCache, config)
            rcache = self._load_cache(ReaderDiskCache, config)

            configs[str(config_filename)] = dict(
                    config=config,
                    config_filename=str(config_filename),
                    ccache=ccache.size if ccache is not None else 0,
                    fcache=fcache.size if fcache is not None else 0,
                    rcache=rcache.size if rcache is not None else 0,
                    )

        #for directory in args.caches_directory:
            #for child in pathlib.Path(directory):
                #if child.is_dir():
                    #try:
                        #ccache = CodebookDiskCache.load_from_path(str(child))
                    #except IOError:
                        #pass
                    #else:
                        #print ccache
                        ##configuration_info.setdefault()

        return (
                ("Configuration File", "RCache", "FCache", "CCache"),
                sorted([(c["config_filename"], c["rcache"], c["fcache"], c["ccache"]) for c in configs.itervalues()])
                )


class ShowConfig(ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowConfig, self).get_parser(prog_name)
        #parser.add_argument("-d", "--caches-directory", dest="caches_directory", default=[".", ], action="append")
        parser.add_argument("config")
        return parser

    @staticmethod
    def _load_cache(cache_class, config):
        try:
            cache = cache_class.from_config(config)
        except IOError as e:
            print e
            return None
        else:
            if cache.exists():
                return cache
            else:
                None

    def take_action(self, args):
        with open(args.config) as fp:
            config = json.load(fp)

        ccache = self._load_cache(CodebookDiskCache, config)
        fcache = self._load_cache(FeatureDiskCache, config)
        rcache = self._load_cache(ReaderDiskCache, config)

        return (
                ("Configuration File", "CCache Path", "CCache Size", "FCache Path", "FCache Size", "RCache Path", "RCache Size"),
                (
                    str(pathlib.Path(args.config).resolve()),
                    str(ccache._cache_directory) if ccache else "",
                    ccache.size if ccache else 0,
                    str(fcache._cache_directory) if fcache else "",
                    fcache.size if fcache else 0,
                    str(rcache._cache_directory) if rcache else "",
                    rcache.size if rcache else 0,
                    ),
                )
