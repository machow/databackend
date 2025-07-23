# Copyright (c) 2024 databackend contributors (MIT License)
#
# See https://github.com/machow/databackend

from __future__ import annotations

import sys
import importlib

from typing import Type, List, Tuple

from abc import ABCMeta


def _load_class(mod_name: str, cls_name: str) -> Type[object]:
    mod = importlib.import_module(mod_name)
    return getattr(mod, cls_name)


class _AbstractBackendMeta(ABCMeta):
    def register_backend(cls, mod_name: str, cls_name: str):
        """Register a backend class to use in issubclass checks.

        This method is similar to the ABCMeta.register method, except that
        it accepts strings, so that an import of the class is not required.

        Note that the arguments to this class match the two pieces in import statements.
        E.g. `from a.b.c import d` would become `mod_name="a.b.c"` and `cls_name="d"`.

        Parameters
        ----------
        mod_name: str
            A module path the class is imported from.
        cls_name: str
            The name of the class in the imported module.
        """
        cls._backends.append((mod_name, cls_name))
        cls._abc_caches_clear()


class AbstractBackend(metaclass=_AbstractBackendMeta):
    """Represent a class, without needing to import it."""

    _backends: List[Tuple[str, str]]

    @classmethod
    def __init_subclass__(cls):
        if not hasattr(cls, "_backends"):
            cls._backends = []

    @classmethod
    def __subclasshook__(cls, subclass: Type[object]):
        for mod_name, cls_name in cls._backends:
            if mod_name not in sys.modules:
                # module isn't loaded, so it can't be the subclass
                # we don't want to import the module to explicitly run the check
                # so skip here.
                continue
            else:
                parent_candidate = _load_class(mod_name, cls_name)
                if issubclass(subclass, parent_candidate):
                    return True

        return NotImplemented


# LazyImport --------
# lazy import class ----

import importlib  # noqa
from types import ModuleType  # noqa


class LazyImport(ModuleType):
    """Lazily represents an imported module.

    Parameters
    ----------
    name :
        The name of the module to import.
    fast :
        If True, the module's attributes will be set on this instance after import, so
        they can be imported without calling this class's `__getattr__` method.

        This assumes that the module does not update its attributes after import.
    debug :
        If True, raise an error instead of importing the module. This allows you to see
        what exactly triggers imports.

    Examples
    --------

    >>> pl = LazyImport("polars")            # no import yet
    >>> def my_func():
    ...     return pl.DataFrame({"x": [1]})  # imports polars on first use
    """

    def __init__(self, name: str, fast: bool = False, debug: bool = False):
        self.__mod: ModuleType | None = None

        self.__name = name
        self.__fast = fast
        self.__debug = debug

    def __getattr__(self, name: str):
        if self.__mod is None:
            self.__mod = self.__import()

        return getattr(self.__mod, name)

    def __import(self) -> ModuleType:
        if self.__debug:
            raise ImportError(
                f"Lazy import of `{self.__name}` is disabled for debugging purposes."
            )

        mod = importlib.import_module(self.__name)

        if self.__fast:
            self.__dict__.update(mod.__dict__)

        return mod
