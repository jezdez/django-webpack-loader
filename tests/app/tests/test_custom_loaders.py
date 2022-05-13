from importlib import reload

from django.test import TestCase

from webpack_loader import config, loader, utils

DEFAULT_CONFIG = "DEFAULT"
LOADER_PAYLOAD = {"status": "done", "chunks": []}


class ValidCustomLoader(loader.WebpackLoader):
    def load_assets(self):
        return LOADER_PAYLOAD


# noinspection PyMethodMayBeStatic
class CustomLoadersTestCase(TestCase):
    def tearDown(self):
        self.reload_webpack()

    def reload_webpack(self):
        """
        Reloads webpack loader modules that have cached values to avoid polluting certain tests
        """
        reload(utils)
        reload(config)

    def test_bad_custom_loader(self):
        """
        Tests that a bad custom loader path will raise an error
        """
        loader_class = "app.tests.bad_loader_path.BadCustomLoader"
        with self.settings(
            WEBPACK_LOADER={
                "DEFAULT": {
                    "CACHE": False,
                    "BUNDLE_DIR_NAME": "django_webpack_loader_bundles/",
                    "LOADER_CLASS": loader_class,
                }
            }
        ):
            self.reload_webpack()
            with self.assertRaises(ImportError, msg="The loader should fail to load with a bad LOADER_CLASS"):
                utils.get_loader(DEFAULT_CONFIG)

    def test_good_custom_loader(self):
        """
        Tests that a good custom loader will return the correct assets
        """
        loader_class = "app.tests.test_custom_loaders.ValidCustomLoader"
        with self.settings(
            WEBPACK_LOADER={
                "DEFAULT": {
                    "CACHE": False,
                    "BUNDLE_DIR_NAME": "django_webpack_loader_bundles/",
                    "LOADER_CLASS": loader_class,
                }
            }
        ):
            self.reload_webpack()
            assets = utils.get_loader(DEFAULT_CONFIG).load_assets()
            self.assertEqual(assets, LOADER_PAYLOAD)
