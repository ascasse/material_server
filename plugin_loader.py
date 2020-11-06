import os
import logging
import pkgutil
import inspect
from pathlib import Path
from importlib import import_module

logger = logging.getLogger(__name__)


def package_dirs(directory):
    """ Return a list of subdirectories of the given one."""
    base_path = Path(".").joinpath(os.path.dirname(__file__), directory)
    return [str(x) for x in base_path.iterdir() if x.is_dir()]


def load_plugins(plugins_dir, plugin_class):
    """ Load all plugins found in subdirectories of the given one

        Parameters
            plugins_dir   -- directory to look inside
            plugin_class  -- the class plugins inherit from
        Returns
            list of instances of the found plugins
    """
    current_path = Path(".").joinpath(os.path.dirname(__file__))
    paths = package_dirs(plugins_dir)
    plugins = []
    for module_info in pkgutil.iter_modules(paths, ""):
        relative_path = Path(module_info.module_finder.path).relative_to(current_path)
        plugin_name = ".".join(relative_path.parts + (module_info.name,))
        if not module_info.ispkg:
            plugin_module = import_module(plugin_name)
            clsmembers = inspect.getmembers(plugin_module, inspect.isclass)
            for (_, clazz) in clsmembers:
                # Add subclasses of the given class, excluding the class itself
                if issubclass(clazz, plugin_class) & (clazz is not plugin_class):
                    logger.info(f"Loading class: {clazz.__module__}.{clazz.__name__}")
                    plugins.append(clazz())
    return plugins
