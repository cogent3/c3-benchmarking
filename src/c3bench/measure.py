import functools
import inspect
import math
import signal
import time
import types
import typing

import cogent3
import numpy
import rich.progress as rp
from pympler import asizeof


class TimeoutError(Exception):
    pass

def format_result(result: typing.Any, num_words: int=5) -> str:
    return " ".join(repr(result).split()[:num_words]).replace("'", "")

def sizeof_db(obj) -> float:
    cur = obj.db.cursor()

    page_count = cur.execute("PRAGMA page_count;").fetchone()[0]
    page_size = cur.execute("PRAGMA page_size;").fetchone()[0]

    result = page_count * page_size
    return result


def timeout(seconds: int):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutError(f"{func.__name__} exceeded {seconds}s")

            # Set the signal handler and an alarm
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)  # cancel alarm

        return wrapper

    return decorator


def record_time_and_size(func: typing.Callable) -> typing.Callable:
    @functools.wraps(func)
    def wrapper(
        *args: typing.Any, **kwargs: typing.Any
    ) -> tuple[typing.Any, float, float]:
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            result = e
        elapsed = time.perf_counter() - start
        sizeof_func = sizeof_db if hasattr(result, "db") else asizeof.asizeof
        try:
            size_bytes = sizeof_func(result)
        except Exception:
            size_bytes = math.nan
        return result, elapsed, size_bytes

    return wrapper


def public_functions(module: types.ModuleType) -> dict[str, object]:
    return {
        name: obj
        for name, obj in inspect.getmembers(module, inspect.isfunction)
        if not name.startswith("_") and obj.__module__ == module.__name__
    }


def calc_stats(func: typing.Callable, n: int, maxtime: int, *args, **kwargs):
    times = []
    sizes = []
    func = timeout(maxtime)(func)
    for _ in range(n):
        result, elapsed, size = func(*args, **kwargs)
        if isinstance(result, Exception):
            return result, math.nan, math.nan, math.nan, math.nan
        times.append(elapsed)
        sizes.append(size)

    times = numpy.array(times)
    sizes = numpy.array(sizes)
    return result, times.mean(), times.std(ddof=1), sizes.mean(), sizes.std(ddof=1)


def run_functions(*, funcs: dict[str, typing.Callable], n: int, maxtime: int, **kwargs):
    results = []
    for name, func in rp.track(funcs.items()):
        result, mean_time, std_time, mean_mem, std_mem = calc_stats(
            func, n, maxtime=maxtime, **kwargs
        )
        if isinstance(result, TimeoutError):
            result = "Timeout"
            print(f"{name!r} time > {maxtime}s")
        elif isinstance(result, Exception):
            print(f"{name!r} raised {result!r}")
            result = format_result(result)
            result = f"Error: {result}..."
        elif isinstance(result, list):
            type_name = result[0].__class__.__name__
            result = f"list({type_name} x {len(result)})"
        else:
            result = result.__class__.__name__

        results.append([name, result, mean_time, std_time, mean_mem, std_mem])

    return cogent3.make_table(
        header=[
            "Function",
            "Result Type",
            "mean(time) seconds",
            "std(time) seconds",
            "mean(RAM)",
            "std(RAM) bytes",
        ],
        data=results,
    )
