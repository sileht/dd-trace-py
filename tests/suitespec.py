from functools import cache
import json
from pathlib import Path
import typing as t


SUITESPECFILE = Path(__file__).parents[1] / "tests" / ".suitespec.json"
SUITESPEC = json.loads(SUITESPECFILE.read_text())


@cache
def get_patterns(suite: str) -> t.Set[str]:
    """Get the patterns for a suite

    >>> sorted(get_patterns("debugger"))  # doctest: +NORMALIZE_WHITESPACE
    ['ddtrace/__init__.py', 'ddtrace/_hooks.py', 'ddtrace/_logger.py', 'ddtrace/_monkey.py', 'ddtrace/auto.py',
    'ddtrace/bootstrap/*', 'ddtrace/commands/*', 'ddtrace/constants.py', 'ddtrace/context.py', 'ddtrace/debugging/*',
    'ddtrace/filter.py', 'ddtrace/internal/*', 'ddtrace/pin.py', 'ddtrace/provider.py', 'ddtrace/sampler.py',
    'ddtrace/settings/__init__.py', 'ddtrace/settings/config.py', 'ddtrace/settings/dynamic_instrumentation.py',
    'ddtrace/settings/exception_debugging.py', 'ddtrace/settings/http.py', 'ddtrace/settings/integration.py',
    'ddtrace/span.py', 'ddtrace/tracer.py', 'riotfile.py', 'scripts/ddtest', 'tests/commands/*', 'tests/debugging/*',
    'tests/integration/*', 'tests/internal/*', 'tests/lib-injection', 'tests/tracer/*']
    >>> get_patterns("foobar")
    set()
    """
    compos = SUITESPEC["components"]
    if suite not in SUITESPEC["suites"]:
        return set()

    suite_patterns = set(SUITESPEC["suites"][suite])

    # Include patterns from include-always components
    for patterns in (patterns for compo, patterns in compos.items() if compo.startswith("$")):
        suite_patterns |= set(patterns)

    def resolve(patterns: set) -> set:
        refs = {_ for _ in patterns if _.startswith("@")}
        resolved_patterns = patterns - refs

        # Recursively resolve references
        for ref in refs:
            try:
                resolved_patterns |= resolve(set(compos[ref[1:]]))
            except KeyError:
                raise ValueError(f"Unknown component reference: {ref}")

        return resolved_patterns

    return resolve(suite_patterns)


def get_suites() -> t.Set[str]:
    """Get the list of suites."""
    return set(SUITESPEC["suites"].keys())
