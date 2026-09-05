# Single source of truth for the version: pyproject.toml reads __version__
# from here, which requires it to stay a plain string literal (setuptools
# parses this file statically, without importing it).
__version__ = '0.2.0'

# format:
# ('spinup_major', 'spinup_minor', 'spinup_patch')
version_info = tuple(int(part) for part in __version__.split('.'))
