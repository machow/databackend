import sys
import importlib

from weakref import WeakKeyDictionary
from abc import ABCMeta


def _load_class(mod_name: str, cls_name: str):
    mod = importlib.import_module(mod_name)
    return getattr(mod, cls_name)


class _AbstractBackendMeta(ABCMeta):
    def __new__(mcls, clsname, bases, attrs):
        cls = super().__new__(mcls, clsname, bases, attrs)
        cls._backends = []
        return cls

    def register_backend(cls, mod_name: str, cls_name: str):
        cls._backends.append((mod_name, cls_name))
        cls._abc_caches_clear()



class AbstractBackend(metaclass=_AbstractBackendMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        print("subclasshook", cls, subclass)
        for mod_name, cls_name in cls._backends:
            if not mod_name in sys.modules:
                continue
            else:
                target_cls = _load_class(mod_name, cls_name)
                if issubclass(target_cls, subclass):
                    return True

        return NotImplemented
