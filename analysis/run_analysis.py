from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "derived"
RESULTS = ROOT / "results"
REFERENCE_LOADS_MW = (50, 100, 250, 400, 500)
BASELINE_LOAD_MW = 250.0
BASELINE_DEMAND_ML_DAY = 17.5


def write_csv(frame: pd.DataFrame, name: str) -> None:
    frame.to_csv(RESULTS / name, index=False)


def annual_reported_water_summary() -> pd.DataFrame:
    water = pd.read_csv(DATA / "reported_us_location_water_2022_2025.csv")
    summary = (
        water.groupby("year", as_index=False)
        .agg(
            locations=("location", "nunique"),
            withdrawal_mg=("withdrawal_mg", "sum"),
            discharge_mg=("discharge_mg", "sum"),
            consumption_mg=("consumption_mg", "sum"),
        )
        .sort_values("year")
    )
    summary["withdrawal_consumed_fraction"] = (
        summary["consumption_mg"] / summary["withdrawal_mg"]
    )
    write_csv(summary, "reported_us_water_summary.csv")
    return summary


def global_accounting_summary() -> pd.DataFrame:
    water = pd.read_csv(DATA / "reported_global_location_water_2025.csv")
    summary = pd.DataFrame(
        [
            {
                "reporting_year": 2025,
                "locations": int(water["location"].nunique()),
                "withdrawal_mg": float(water["withdrawal_mg"].sum()),
                "discharge_mg": float(water["discharge_mg"].sum()),
                "consumption_mg": float(water["consumption_mg"].sum()),
            }
        ]
    )
    summary["withdrawal_consumed_fraction"] = (
        summary["consumption_mg"] / summary["withdrawal_mg"]
    )
    write_csv(summary, "reported_global_water_summary_2025.csv")
    return summary


def facility_water_electricity_summary() -> pd.DataFrame:
    facility = pd.read_csv(DATA / "facility_water_electricity_2019_2024.csv")
    ordered = facility.sort_values(["location", "year"]).copy()
    ordered["annual_intensity_change_l_per_total_kwh"] = ordered.groupby("location")[
        "withdrawal_intensity_l_per_total_kwh"
    ].diff()
    write_csv(ordered, "facility_water_electricity_trends.csv")
    return ordered


def regional_efficiency_summary() -> pd.DataFrame:
    regional = pd.read_csv(DATA / "regional_pue_wue_2022_2025.csv")
    regional["pue_change_2024_2025"] = regional["pue_2025"] - regional["pue_2024"]
    regional["wue_change_2024_2025"] = regional["wue_2025"] - regional["wue_2024"]
    write_csv(regional, "regional_pue_wue_changes.csv")
    return regional


def source_flow_results() -> tuple[pd.DataFrame, pd.DataFrame]:
    source_flow = pd.read_csv(DATA / "source_flow_results_10_systems.csv")
    equal = pd.read_csv(DATA / "equal_demand_source_flow_10_systems.csv")
    if source_flow["location"].nunique() != 10 or len(source_flow) != 20:
        raise RuntimeError("Expected a balanced 10-location by 2-architecture result table")
    if equal["location"].nunique() != 10 or len(equal) != 10:
        raise RuntimeError("Expected ten equal-demand source-flow rows")

    ranking = equal.sort_values("pressure_p95_pct", ascending=False).reset_index(drop=True)
    ranking.insert(0, "pressure_rank", np.arange(1, len(ranking) + 1))
    write_csv(ranking, "equal_demand_source_flow_ranking.csv")

    sensitivity_rows: list[dict[str, object]] = []
    for load_mw in REFERENCE_LOADS_MW:
        demand_ml_day = BASELINE_DEMAND_ML_DAY * load_mw / BASELINE_LOAD_MW
        for row in equal.itertuples(index=False):
            sensitivity_rows.append(
                {
                    "location": row.location,
                    "location_label": row.location_label,
                    "source_component": row.source_component,
                    "source_fraction": row.source_fraction,
                    "reference_it_load_mw": load_mw,
                    "modeled_consumptive_demand_ml_day": demand_ml_day,
                    "pressure_p95_pct": row.pressure_p95_pct * load_mw / BASELINE_LOAD_MW,
                    "hydrology_source_id": row.hydrology_source_id,
                }
            )
    sensitivity = pd.DataFrame(sensitivity_rows)
    write_csv(sensitivity, "reference_load_sensitivity_50_500_mw.csv")
    return ranking, sensitivity


def near_equal_demand_summary() -> pd.DataFrame:
    pairs = pd.read_csv(DATA / "near_equal_monthly_pair_distribution.csv")
    summary = pd.DataFrame(
        [
            {
                "eligible_pairs": int(len(pairs)),
                "pressure_ratio_q25": float(pairs["pressure_ratio"].quantile(0.25)),
                "pressure_ratio_median": float(pairs["pressure_ratio"].median()),
                "pressure_ratio_q75": float(pairs["pressure_ratio"].quantile(0.75)),
                "pressure_ratio_max": float(pairs["pressure_ratio"].max()),
                "eligibility_rule": "different locations; monthly modeled consumption differs by no more than 3%",
            }
        ]
    )
    write_csv(summary, "near_equal_demand_summary.csv")
    return summary


def headline_statistics(
    annual: pd.DataFrame,
    global_summary: pd.DataFrame,
    facility: pd.DataFrame,
    regional: pd.DataFrame,
    ranking: pd.DataFrame,
    sensitivity: pd.DataFrame,
    near_equal: pd.DataFrame,
) -> dict[str, object]:
    audit = pd.read_csv(DATA / "source_system_audit.csv")
    central = pd.read_csv(DATA / "location_architecture_decomposition.csv")
    central_p95 = central[(central["practice"] == "central") & (central["quantile"] == 0.95)].iloc[0]
    latest = annual.loc[annual["year"].idxmax()]
    global_latest = global_summary.iloc[0]
    facility_positive = facility.loc[
        facility["withdrawal_intensity_l_per_total_kwh"] > 0,
        "withdrawal_intensity_l_per_total_kwh",
    ]
    spread = float(ranking["pressure_p95_pct"].max() / ranking["pressure_p95_pct"].min())
    load_spreads = sensitivity.groupby("reference_it_load_mw")["pressure_p95_pct"].agg(
        lambda values: values.max() / values.min()
    )

    stats: dict[str, object] = {
        "study_scope": {
            "audited_locations": int(audit["candidate_location"].nunique()),
            "source_flow_systems": int(ranking["location"].nunique()),
            "source_flow_record_end": "2025-09-30",
        },
        "reported_water": {
            "us_location_year_observations": int(
                len(pd.read_csv(DATA / "reported_us_location_water_2022_2025.csv"))
            ),
            "us_locations_in_2025": int(latest["locations"]),
            "us_2025_withdrawal_mg": float(latest["withdrawal_mg"]),
            "us_2025_consumption_mg": float(latest["consumption_mg"]),
            "global_locations_in_2025": int(global_latest["locations"]),
            "global_2025_withdrawal_mg": float(global_latest["withdrawal_mg"]),
            "global_2025_consumption_mg": float(global_latest["consumption_mg"]),
        },
        "source_flow": {
            "common_demand_ml_day": BASELINE_DEMAND_ML_DAY,
            "minimum_p95_pct": float(ranking["pressure_p95_pct"].min()),
            "minimum_location": str(ranking.loc[ranking["pressure_p95_pct"].idxmin(), "location_label"]),
            "maximum_p95_pct": float(ranking["pressure_p95_pct"].max()),
            "maximum_location": str(ranking.loc[ranking["pressure_p95_pct"].idxmax(), "location_label"]),
            "cross_system_p95_spread": spread,
            "reference_loads_mw": list(REFERENCE_LOADS_MW),
            "reference_load_spread_min": float(load_spreads.min()),
            "reference_load_spread_max": float(load_spreads.max()),
            "central_p95_location_percent": float(central_p95["location_percent"]),
            "central_p95_architecture_percent": float(central_p95["architecture_percent"]),
            "central_p95_interaction_residual_percent": float(
                central_p95["interaction_residual_percent"]
            ),
            "near_equal_monthly_pairs": int(near_equal.iloc[0]["eligible_pairs"]),
            "near_equal_pressure_ratio_median": float(
                near_equal.iloc[0]["pressure_ratio_median"]
            ),
        },
        "facility_water_electricity": {
            "observations": int(len(facility)),
            "facilities": int(facility["location"].nunique()),
            "positive_intensity_min_l_per_total_kwh": float(facility_positive.min()),
            "positive_intensity_max_l_per_total_kwh": float(facility_positive.max()),
        },
        "regional_efficiency": {
            "matched_regions": int(len(regional)),
            "regions_with_lower_2025_wue": int((regional["wue_change_2024_2025"] < 0).sum()),
            "wue_change_min": float(regional["wue_change_2024_2025"].min()),
            "wue_change_max": float(regional["wue_change_2024_2025"].max()),
        },
    }
    (RESULTS / "headline_statistics.json").write_text(
        json.dumps(stats, indent=2) + "\n", encoding="utf-8"
    )
    return stats


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    annual = annual_reported_water_summary()
    global_summary = global_accounting_summary()
    facility = facility_water_electricity_summary()
    regional = regional_efficiency_summary()
    ranking, sensitivity = source_flow_results()
    near_equal = near_equal_demand_summary()
    stats = headline_statistics(
        annual, global_summary, facility, regional, ranking, sensitivity, near_equal
    )
    print(json.dumps(stats["source_flow"], indent=2))


if __name__ == "__main__":
    main()
