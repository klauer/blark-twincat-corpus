import dataclasses
import pathlib

from multiprocessing import Pool

import blark


@dataclasses.dataclass
class Result:
    tsproj: pathlib.Path
    num_parsed: int = 0
    num_failures: int = 0
    failed_files: list[tuple[pathlib.Path, str]] = dataclasses.field(
        default_factory=list
    )
    ex: Exception | None = None


def parse_tsproj(tsproj: pathlib.Path) -> Result:
    print("Parsing:", tsproj)
    try:
        res = list(blark.parse_project(tsproj))
    except Exception as ex:
        print("Parsing failed for project:", tsproj, ex)
        return Result(tsproj=tsproj, ex=ex)
    return Result(
        tsproj=tsproj,
        num_parsed=sum(1 for parsed in res if parsed.exception is None),
        failed_files=[
            (parsed.filename, str(parsed.exception))
            for parsed in res
            if parsed.exception is not None and parsed.filename is not None
        ],
    )


corpus_root = pathlib.Path(__file__).resolve().absolute().parent
tsprojects = list(corpus_root.glob("**/*.tsproj", case_sensitive=False))


if __name__ == "__main__":
    with Pool(processes=10) as pool:
        results = pool.map(parse_tsproj, tsprojects)
        print("Total projects:", len(results))
        print("Total files parsed:", sum(res.num_parsed for res in results))
        print(
            "Total files with failures:", sum(len(res.failed_files) for res in results)
        )
        print(
            "Successfully parsed projects:",
            len([res for res in results if res.ex is None]),
        )
        failures = [res for res in results if res.ex is not None]
        print(f"Failed projects: ({len(failures)})")
        for res in failures:
            print(res.tsproj)
        print("Failed files:")
        for res in results:
            if res.failed_files:
                print()
                print(res.tsproj)
            for fn, ex in res.failed_files:
                print(fn, str(ex).splitlines()[0])
