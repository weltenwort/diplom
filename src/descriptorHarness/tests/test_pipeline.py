import unittest

from descriptorHarness.utils import ProcessPipeline


def step_1(args):
    data, proxy = args
    proxy.report(data)
    return data + 1


def step_2(args):
    data, proxy = args
    return data ** 2


class Reporter(object):
    def __init__(self):
        self.memory = []

    def report(self, data):
        self.memory.append(data)

    def get_memory(self):
        return self.memory


class TestProcessPipeline(unittest.TestCase):
    def test_simple(self):
        pipeline = ProcessPipeline([
            (step_1, "default"),
            (step_2, "default"),
            ],
            proxy_factory=Reporter,
            )
        result = set(pipeline.start(range(5)))

        self.assertEqual(result, set([1, 4, 9, 16, 25]))
        self.assertEqual(pipeline.proxy.get_memory(), range(5))
