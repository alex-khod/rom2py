import unittest


# def change_resources_root():
#     from src import resources
#     resources.get_root = lambda: ".."


class TestCase(unittest.TestCase):
    pass

    # seems better to define root directory as default working directory for running tests

    # def __init__(self, methodName="runTest"):
    #     super().__init__(methodName)
    # change_resources_root()
