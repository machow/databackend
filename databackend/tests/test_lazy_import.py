from databackend import LazyImport
import sys


def test_lazy_import():
    mod_name = "databackend.tests.an_unimported_module"
    data_mod = LazyImport(mod_name)

    assert mod_name not in sys.modules
    data_mod.UnimportedClass

    assert mod_name in sys.modules
    del sys.modules[mod_name]
