# SPDX-FileCopyrightText: 2017-2023 The PyPSA-Eur Authors
#
# SPDX-License-Identifier: MIT

from pathlib import Path
import yaml
import difflib
import requests
from tqdm import tqdm

def progress_retrieve(url, file, disable=False):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    # Hotfix - Bug, tqdm not working with disable=False
    disable = True

    if disable:
        response = requests.get(url, headers=headers, stream=True)
        with open(file, "wb") as f:
            f.write(response.content)
    else:
        response = requests.get(url, headers=headers, stream=True)
        total_size = int(response.headers.get("content-length", 0))
        chunk_size = 1024

        with tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=str(file),
        ) as t:
            with open(file, "wb") as f:
                for data in response.iter_content(chunk_size=chunk_size):
                    f.write(data)
                    t.update(len(data))

def load_yaml(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def compare_yaml(file1, file2):
    yaml1 = load_yaml("path/to/file1.yaml")
    yaml2 = load_yaml("path/to/file2.yaml")

    yaml1_lines = yaml.dump(yaml1).splitlines()
    yaml2_lines = yaml.dump(yaml2).splitlines()

    diff = difflib.unified_diff(
        yaml1_lines, yaml2_lines, lineterm="", fromfile=file1, tofile=file2
    )

    for line in diff:
        print(line)


# compare_yaml("file1.yaml", "file2.yaml")


def mock_snakemake(rulename, **wildcards):
    """
    This function is expected to be executed from the 'scripts'-directory of '
    the snakemake project. It returns a snakemake.script.Snakemake object,
    based on the Snakefile.

    If a rule has wildcards, you have to specify them in **wildcards.

    Parameters
    ----------
    rulename: str
        name of the rule for which the snakemake object should be generated
    **wildcards:
        keyword arguments fixing the wildcards. Only necessary if wildcards are
        needed.
    """
    import snakemake as sm
    import os
    from pypsa.descriptors import Dict
    from snakemake.script import Snakemake
    from packaging.version import Version, parse

    script_dir = Path(__file__).parent.resolve()
    # comment for a debug
    assert (
        Path.cwd().resolve() == script_dir
    ), f"mock_snakemake has to be run from the repository scripts directory {script_dir}"
    os.chdir(script_dir.parent)
    for p in sm.SNAKEFILE_CHOICES:
        if os.path.exists(p):
            snakefile = p
            break

    kwargs = dict(rerun_triggers=[]) if parse(sm.__version__) > Version("7.7.0") else {}
    workflow = sm.Workflow(snakefile, overwrite_configfiles=[], **kwargs)

    workflow.include(snakefile)
    workflow.global_resources = {}
    rule = workflow.get_rule(rulename)
    dag = sm.dag.DAG(workflow, rules=[rule])
    wc = Dict(wildcards)
    job = sm.jobs.Job(rule, dag, wc)

    def make_accessable(*ios):
        for io in ios:
            for i in range(len(io)):
                io[i] = os.path.abspath(io[i])

    make_accessable(job.input, job.output, job.log)
    snakemake = Snakemake(
        job.input,
        job.output,
        job.params,
        job.wildcards,
        job.threads,
        job.resources,
        job.log,
        job.dag.workflow.config,
        job.rule.name,
        None,
    )
    # create log and output dir if not existent
    for path in list(snakemake.log) + list(snakemake.output):
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    os.chdir(script_dir)
    return snakemake
