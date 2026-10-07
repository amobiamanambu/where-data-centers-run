from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "derived"
RESULTS = ROOT / "results"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    audit = pd.read_csv(DATA / "source_system_audit.csv")
    source_flow = pd.read_csv(DATA / "source_flow_results_10_systems.csv")
    sensitivity = pd.read_csv(RESULTS / "reference_load_sensitivity_50_500_mw.csv")
    headline = json.loads((RESULTS / "headline_statistics.json").read_text(encoding="utf-8"))

    require(len(audit) == 20, "The source-system audit must contain 20 rows")
    require(audit["candidate_location"].nunique() == 20, "Audit locations must be unique")
    require(source_flow["location"].nunique() == 10, "Expected ten source-flow systems")
    require(
        set(source_flow.groupby("location")["architecture_id"].nunique()) == {2},
        "Each source-flow system must contain both cooling architectures",
    )
    require(
        sorted(sensitivity["reference_it_load_mw"].unique().tolist())
        == [50, 100, 250, 400, 500],
        "The reference-load sensitivity must cover 50, 100, 250, 400 and 500 MW",
    )
    require(len(sensitivity) == 50, "Expected ten systems at five reference loads")

    pivot = sensitivity.pivot(
        index="location", columns="reference_it_load_mw", values="pressure_p95_pct"
    )
    require(
        np.allclose(pivot[500] / pivot[50], 10.0, rtol=0, atol=1e-10),
        "The 50–500 MW sensitivity must scale linearly",
    )
    require(
        abs(headline["source_flow"]["minimum_p95_pct"] - 0.02455915862446552)
        < 1e-12,
        "Kansas City lower endpoint changed unexpectedly",
    )
    require(
        abs(headline["source_flow"]["maximum_p95_pct"] - 25.545910532949616)
        < 1e-12,
        "Forest City upper endpoint changed unexpectedly",
    )
    require(
        abs(headline["source_flow"]["central_p95_location_percent"] - 93.6572212159243)
        < 1e-10,
        "Location variance contribution changed unexpectedly",
    )

    forbidden = (
        "manuscript",
        "tracked",
        "track changes",
        "sync_living",
        "page snapshot",
        ".docx",
        "earth futures",
    )
    text_files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".py", ".json", ".csv", ".cff", ".txt"}
    ]
    hits: list[str] = []
    for path in text_files:
        if path.resolve() == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for term in forbidden:
            if term in text:
                hits.append(f"{path.relative_to(ROOT)}: {term}")
    require(not hits, "Editorial or document-production artifacts found: " + "; ".join(hits))
    print("PASS: release contents and headline results verified.")


if __name__ == "__main__":
    main()
