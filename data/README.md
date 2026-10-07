# Data guide

All files in this directory are machine-readable research data retained for the published analysis workflow.

## `derived/`

- `reported_us_location_water_2022_2025.csv`: U.S. location-year withdrawal, discharge, estimated consumption, geographic screening variables, and source locators.
- `reported_global_location_water_2025.csv`: global 2025 location comparison at the original reporting boundary.
- `facility_water_electricity_2019_2024.csv`: facility withdrawal and total-facility electricity observations.
- `regional_pue_wue_2022_2025.csv`: matched regional PUE and WUE values.
- `reported_source_mix_2022_2025.csv`: reported potable and reclaimed-water components where available.
- `source_system_audit.csv`: evidence decisions for 20 operating locations.
- `source_flow_results_10_systems.csv`: two cooling architectures evaluated for ten documented source systems.
- `equal_demand_source_flow_10_systems.csv`: common 17.5 ML d⁻¹ comparison.
- `cooling_model_monthly_10_systems.csv`: frozen monthly cooling-model output used by the hydrological analysis.
- `near_equal_monthly_pair_distribution.csv`: descriptive comparison of monthly cases whose modeled consumption differs by no more than 3%.
- `expanded_flow_record_quality.csv`: record completeness for the four added source systems.
- `common_period_sensitivity.csv`: comparison using the common 27-water-year period.
- `location_architecture_decomposition.csv`: descriptive variance decomposition for location, cooling architecture, and their interaction/residual.
- `managed_system_cases.csv`: municipal, reuse, and source-family cases whose accounting boundaries are not pooled.

## `provenance/`

`source_register.csv` links stable source identifiers to bibliographic information, public URLs, exact locators, verification notes, and analytical boundaries.

## Interpretation

Source-flow percentages compare a specified consumptive demand with a documented hydrological record. They are not estimates of facility impact, water rights, utility headroom, ecological-flow compliance, or available supply. Corporate and utility quantities retain the definitions of their original sources and should not be pooled when their denominators or system boundaries differ.
