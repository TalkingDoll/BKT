"""Read-only access to the notebook definitions and content-addressed caches.

Loading this module does not execute notebook setup, experiments, recorders or
file writers. Numerical definitions retain their original bytecode so cache
keys agree with the notebook under the recorded Python/NumPy/SciPy versions.
"""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CacheMissError(FileNotFoundError):
    """A requested notebook cache is unavailable; no computation was started."""

    def __init__(self, entry):
        self.entry = entry
        super().__init__(f"Notebook cache miss: {entry['name']} -> {entry['path']}")


class CacheReadError(RuntimeError):
    """An existing notebook cache could not be decoded safely."""


_IMPORT_ROOTS = {
    "sys", "os", "time", "json", "math", "pathlib", "collections",
    "functools", "hashlib", "tempfile", "types", "zipfile", "numpy",
    "scipy", "itertools",
}
_SETTINGS = {
    "QUICK", "PARTS", "NPAIR", "M2D", "M10D", "SEEDS_MAIN", "SEEDS_SEC",
    "SEEDS_10D", "DT", "DT_A2", "TUNE", "R10", "RUN_A10_DICTIONARY_SCAN",
    "TRAINING_BUDGETS", "FIXED_TRAINING_PAIRS", "APPENDIX_SYSTEMS", "RETAINED_SYSTEMS",
    "REFERENCE_REPEATS", "CACHE_ENABLED", "CACHE_DIR", "STATS", "DTSIM",
    "TAU", "_POTENTIAL_CACHE_COMPATIBILITY", "_rr_init",
}
_CELL4_FUNCTIONS = {
    "source_A", "make_dict", "training_data", "fit_for", "learned_transport",
    "evaluate_learned", "score", "summarize_method",
}


def _target_names(target):
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.Tuple, ast.List)):
        return set().union(*(_target_names(item) for item in target.elts))
    return set()


def _safe_assignment(node):
    if not isinstance(node, ast.Assign):
        return False
    # Preserve the existing cached estimator adapter without fitting anything.
    if len(node.targets) == 1 and isinstance(node.targets[0], ast.Attribute):
        target = node.targets[0]
        return (
            isinstance(target.value, ast.Name)
            and target.value.id == "RREstimate"
            and target.attr == "__init__"
            and isinstance(node.value, ast.Name)
            and node.value.id == "_cached_rr_init"
        )
    names = set().union(*(_target_names(target) for target in node.targets))
    if not names or not names <= _SETTINGS:
        return False
    # The two constructors below create only an in-memory path/counter.
    for descendant in ast.walk(node.value):
        if isinstance(descendant, ast.Call):
            if not isinstance(descendant.func, ast.Name) or descendant.func.id not in {"Path", "Counter"}:
                raise ValueError(f"Unexpected call in notebook setting {sorted(names)}")
    return True


def _readonly_reference_definition(node):
    """Remove only the reference sidecar write; preserve its cache-key formula."""
    node = copy.deepcopy(node)
    body = []
    removed = 0
    for statement in node.body:
        if (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Call)
            and isinstance(statement.value.func, ast.Attribute)
            and statement.value.func.attr == "write_text"
        ):
            receiver = statement.value.func.value
            if (
                isinstance(receiver, ast.Call)
                and isinstance(receiver.func, ast.Name)
                and receiver.func.id == "Path"
                and len(receiver.args) == 1
                and isinstance(receiver.args[0], ast.Constant)
                and receiver.args[0].value == "reference_statistics.json"
            ):
                removed += 1
                continue
            raise ValueError("Unexpected writer in reference_statistics")
        body.append(statement)
    if removed != 1:
        raise ValueError("Expected exactly one reference-statistics sidecar writer")
    node.body = body
    return node


def _selected_nodes(cell_index, tree, namespace):
    selected = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            aliases = [alias for alias in node.names if alias.name.split(".")[0] in _IMPORT_ROOTS]
            if aliases:
                selected.append(ast.copy_location(ast.Import(names=aliases), node))
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in _IMPORT_ROOTS:
                selected.append(node)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if node.name in {"_Recorder", "section", "save_json"}:
                continue
            if cell_index == 4 and node.name not in _CELL4_FUNCTIONS:
                continue
            selected.append(_readonly_reference_definition(node) if node.name == "reference_statistics" else node)
        elif _safe_assignment(node):
            selected.append(node)
        elif (
            cell_index == 1 and isinstance(node, ast.If)
            and isinstance(node.test, ast.Name) and node.test.id == "QUICK"
        ):
            # This is the notebook's constants-only QUICK/full budget branch.
            for child in node.body + node.orelse:
                if not _safe_assignment(child):
                    raise ValueError("Unexpected operation in notebook budget branch")
            selected.append(node)
    return selected


def cache_entry(namespace, name, key):
    """Return the exact notebook cache key and path without reading its arrays."""
    config = {
        "format": 1, "python": sys.version_info[:2],
        "numpy": namespace["np"].__version__, "scipy": namespace["scipy"].__version__,
        "parameters": key,
    }
    digest = namespace["digest"](config)
    path = namespace["CACHE_DIR"] / name / (digest + ".npz")
    return {
        "name": name, "digest": digest, "path": str(path), "exists": path.is_file(),
        "configuration": namespace["_identity"](config),
    }


def load_notebook_api(notebook_path=None, output_dir=None, *, fail_on_cache_miss=True,
                      require_compatible_runtime=True):
    """Return notebook functions/constants with read-only numerical-cache access.

    Default cache misses raise before simulation or fitting. Setting
    ``fail_on_cache_miss=False`` permits explicit caller-triggered computation
    in memory only; it still never writes the original cache or sidecar files.
    The loader does not change cwd. ``output_dir`` defaults to project/outputs.
    ``_rr_init`` is the original uncached estimator initializer for timed fits.
    """
    notebook_path = Path(notebook_path or ROOT / "BKT_experiments.ipynb").resolve()
    project_dir = notebook_path.parent
    output_dir = Path(output_dir or project_dir / "outputs").resolve()
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    namespace = {
        "__name__": "comparison_notebook_definitions",
        "PROJECT_DIR": project_dir, "OUTPUT_DIR": output_dir,
    }
    definitions = []
    for cell_index in (1, 2, 3, 4):
        cell = notebook["cells"][cell_index]
        if cell["cell_type"] != "code":
            raise ValueError(f"Expected notebook code cell {cell_index}")
        tree = ast.parse("".join(cell["source"]), filename=str(notebook_path))
        nodes = _selected_nodes(cell_index, tree, namespace)
        # IPython compiles top-level statements separately. Compiling imports
        # together with functions can change CPython's LOAD_METHOD/LOAD_ATTR
        # bytecode choices and therefore the notebook's content-addressed keys.
        for node in nodes:
            module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
            exec(compile(module, str(notebook_path), "exec", dont_inherit=True), namespace)
        definitions.extend(node.name for node in nodes if isinstance(node, (ast.FunctionDef, ast.ClassDef)))

    np, scipy = namespace["np"], namespace["scipy"]
    runtime = {"python": list(sys.version_info[:2]), "numpy": np.__version__, "scipy": scipy.__version__}
    if require_compatible_runtime and runtime != {"python": [3, 11], "numpy": "2.4.6", "scipy": "1.17.1"}:
        raise RuntimeError(f"Notebook cache runtime must be Python 3.11 / NumPy 2.4.6 / SciPy 1.17.1; got {runtime}")
    namespace["CACHE_DIR"] = output_dir / "cache" / "numerics"
    namespace["REFERENCE_RESULTS"] = {}
    events = []

    def readonly_cached_arrays(name, key, compute):
        entry = cache_entry(namespace, name, key)
        if entry["exists"]:
            try:
                with np.load(entry["path"], allow_pickle=False) as arrays:
                    stored_config = json.loads(str(arrays["config"]))
                    if namespace["digest"](stored_config) != entry["digest"]:
                        raise ValueError("Stored cache configuration does not match its requested key")
                    value = namespace["_unpack"](json.loads(str(arrays["metadata"])), arrays)
            except (ValueError, OSError, KeyError, EOFError, namespace["zipfile"].BadZipFile) as error:
                events.append(dict(entry, status="invalid"))
                raise CacheReadError(f"Cannot decode notebook cache {entry['path']}") from error
            namespace["STATS"][f"{name}:hit"] += 1
            events.append(dict(entry, status="hit"))
            return value
        namespace["STATS"][f"{name}:miss"] += 1
        events.append(dict(entry, status="miss"))
        if fail_on_cache_miss:
            raise CacheMissError(entry)
        return compute()

    def disabled_writer(*args, **kwargs):
        raise RuntimeError("Notebook output writers are disabled by the comparison loader")

    namespace["cached_arrays"] = readonly_cached_arrays
    namespace["save_json"] = disabled_writer
    namespace["_loader_metadata"] = {
        "notebook": str(notebook_path), "output_directory": str(output_dir),
        "runtime": runtime, "read_only_cache": True,
        "fail_on_cache_miss": bool(fail_on_cache_miss),
        "loaded_definitions": definitions,
        "reference_statistics_sidecar_write_removed": True,
        "cache_events": events,
    }
    required = {"Potential", "Dictionary", "RREstimate", "_rr_init", "source_A",
                "simulate_pairs", "stationary_samples", "reference_for_potential",
                "transport", "sliced_w2", "reference_statistics", "cached_arrays"}
    missing = required - namespace.keys()
    if missing:
        raise ValueError(f"Notebook API definitions missing: {sorted(missing)}")
    return namespace


def probe_cache_call(namespace, function, *args, **kwargs):
    """Inspect the first cache lookup in a call, without loading or computing.

    Do not share the same namespace across concurrent probes/calls: the cache
    hook is temporarily replaced. Source/key preparation before a lookup still
    runs, so use this for the documented trajectory/reference/FD entry points.
    """
    class ProbeStop(Exception):
        pass

    found = []
    original = namespace["cached_arrays"]

    def probe(name, key, compute):
        found.append(cache_entry(namespace, name, key))
        raise ProbeStop

    namespace["cached_arrays"] = probe
    try:
        (namespace[function] if isinstance(function, str) else function)(*args, **kwargs)
    except ProbeStop:
        return found[0]
    finally:
        namespace["cached_arrays"] = original
    raise ValueError("The requested call did not access a numerical cache")


def probe_equal_data_inputs(namespace, betas=(0.0, 0.5), training_seeds=range(100, 105),
                            pairs=200000, particles=2000):
    """Enumerate paired-study training, target, reference and FD cache keys.

    No simulation, fitting, target generation or training-array loading occurs.
    Source sample seeds are recorded; generating their 2000-point clouds is
    inexpensive and intentionally left to the caller.
    """
    np = namespace["np"]
    entries = []
    for beta in betas:
        pot = namespace["Potential"]("A", d=2, beta=float(beta))
        for seed in training_seeds:
            entry = probe_cache_call(namespace, "simulate_pairs", pot, pairs, np.random.default_rng(seed))
            entries.append(dict(entry, role="training", beta=float(beta), training_seed=seed,
                                source_seed=500 + seed - 100))
        entry = probe_cache_call(namespace, "stationary_samples", pot, particles, np.random.default_rng(7))
        entries.append(dict(entry, role="fixed_target", beta=float(beta), target_seed=7))
        entry = probe_cache_call(namespace, "reference_for_potential", pot, particles, f"A2_beta{float(beta)}")
        entries.append(dict(entry, role="ten_reference_pairs", beta=float(beta)))
        entry = probe_cache_call(namespace, "exact_2d", pot, n=201, kmax=129)
        entries.append(dict(entry, role="fd_spectrum", beta=float(beta)))
    return entries


if __name__ == "__main__":
    # Definition/provenance smoke test and metadata-only cache inventory.
    from experiment_store import managed_outputs
    with managed_outputs("double_well"):
        api = load_notebook_api()
        entries = probe_equal_data_inputs(api)
        print(json.dumps({
            "runtime": api["_loader_metadata"]["runtime"],
            "potential_version": api["potential_cache_version"](),
            "lookup_count": len(entries), "existing_count": sum(row["exists"] for row in entries),
            "lookups": [{key: value for key, value in row.items() if key != "configuration"} for row in entries],
        }, indent=2))
