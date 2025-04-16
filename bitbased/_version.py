"""A temporary file that gives you the correct version even during develpoment.

The call to _guess_version will be replaced with a
 hardcoded version number in any wheels or sdists.
"""


def _guess_version() -> str:
    """Only ever called when working from the VCS source tree"""
    import os
    import warnings
    from pathlib import Path

    if os.environ.get("DEV_QUICKLOAD"):
        return "DEV_QUICKLOAD_VERSION_SUPPRESSED"

    vcs_root = Path(__file__).parents[1]

    try:
        import versioningit

        return versioningit.get_version(vcs_root) + "-EDITABLE"
    except Exception as exc:
        warnings.warn(
            f"Version not set! Got exception '{exc.__class__.__name__}: {exc}'"
        )
        return "VERSION_ERROR"


# This next line will be replaced in build artifacts.
# DO NOT CHANGE IT!
# It must match the regex in the pyproject.toml
# [tool.versioningit.onbuild.regex] field
__version__ = _guess_version()
