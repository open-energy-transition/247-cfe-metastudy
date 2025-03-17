# SPDX-FileCopyrightText: Contributors to PyPSA-Eur <https://github.com/pypsa/pypsa-eur>
#
# SPDX-License-Identifier: MIT
"""
Retrieve cost data from ``technology-data``.
"""

import logging
from pathlib import Path
from _helpers import progress_retrieve

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if "snakemake" not in globals():
        from _helpers import mock_snakemake

        snakemake = mock_snakemake("retrieve_cost_data", year=2030)
        rootpath = ".."
    else:
        rootpath = "."

    version = snakemake.params.version
    if "/" in version:
        baseurl = f"https://raw.githubusercontent.com/{version}/outputs/"
    else:
        baseurl = f"https://raw.githubusercontent.com/PyPSA/technology-data/{version}/outputs/"
    filepath = Path(snakemake.output[0])
    url = baseurl + filepath.name

    print(url)

    to_fn = Path(rootpath) / filepath

    print(to_fn)

    logger.info(f"Downloading technology data from '{url}'.")
    disable_progress = False
    progress_retrieve(url, to_fn, disable=disable_progress)

    logger.info(f"Technology data available at at {to_fn}")