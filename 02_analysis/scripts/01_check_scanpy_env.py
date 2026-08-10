from __future__ import annotations

import importlib
import platform
import sys


REQUIRED_MODULES = [
    "scanpy",
    "anndata",
    "pandas",
    "numpy",
    "scipy",
    "matplotlib",
    "seaborn",
    "sklearn",
    "statsmodels",
    "igraph",
    "leidenalg",
    "harmonypy",
    "h5py",
]

OPTIONAL_MODULES = [
    "gseapy",
]


def main() -> None:
    print("Python:", sys.executable)
    print("Version:", sys.version.replace("\n", " "))
    print("Platform:", platform.platform())
    print("")
    missing_required: list[str] = []
    missing_optional: list[str] = []
    for name in REQUIRED_MODULES:
        try:
            mod = importlib.import_module(name)
            version = getattr(mod, "__version__", "ok")
            print(f"{name}: {version}")
        except Exception as exc:  # pragma: no cover - diagnostic script
            missing_required.append(name)
            print(f"{name}: MISSING ({exc})")

    print("\nOptional modules:")
    for name in OPTIONAL_MODULES:
        try:
            mod = importlib.import_module(name)
            version = getattr(mod, "__version__", "ok")
            print(f"{name}: {version}")
        except Exception as exc:  # pragma: no cover - diagnostic script
            missing_optional.append(name)
            print(f"{name}: OPTIONAL MISSING ({exc})")

    if missing_required:
        raise SystemExit(f"Missing required modules: {', '.join(missing_required)}")
    if missing_optional:
        print(f"\nOptional modules missing or broken: {', '.join(missing_optional)}")
        print("This is acceptable for Phase 1. Enrichment analysis can be repaired later.")
    print("\nEnvironment check passed for Phase 1.")


if __name__ == "__main__":
    main()
