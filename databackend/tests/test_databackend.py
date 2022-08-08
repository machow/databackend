import pytest
import sys
import importlib

from databackend import AbstractBackend
from databackend.tests.a_data_class import ADataClass

@pytest.fixture
def Base():
    class Base(AbstractBackend):
        pass

    Base.register_backend("databackend.tests.a_data_class", "ADataClass")

    return Base


def test_check_unimported_mod(Base):
    class ABase(AbstractBackend): pass

    mod_name = "databackend.tests.an_unimported_module"
    ABase.register_backend(mod_name, "UnimportedClass")

    # check pre-import and verify it's still not imported ----
    assert not issubclass(int, ABase)
    assert mod_name not in sys.modules

    # do import and verify ABC is seen as parent class ----
    mod = importlib.import_module(mod_name)

    assert issubclass(mod.UnimportedClass, ABase)


def test_issubclass(Base):
    assert issubclass(ADataClass, Base)


def test_isinstance(Base):
    assert isinstance(ADataClass(), Base)
    

def test_check_is_cached():
    checks = [0]

    class ABase(AbstractBackend):
        @classmethod
        def __subclasshook__(cls, subclass):
            # increment the number in checks, as a dumb way
            # of seeing how often this runs
            # could also use abc.ABCMeta._dump_registry
            checks[0] = checks[0] + 1
            return super().__subclasshook__(subclass)

    # this check runs subclasshook ----
    issubclass(ADataClass, ABase)
    assert checks[0] == 1

    # now that ADataClass is in the abc.ABCMeta cache, it
    # does *not* run subclasshook
    issubclass(ADataClass, ABase)
    assert checks[0] == 1


