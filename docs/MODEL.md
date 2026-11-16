# Radial DC constant-power model v1

## Network assumptions

One ideal stiff DC source supplies a rooted tree. Each load node has exactly one parent, a nonnegative constant-power demand, and one nonnegative total DC loop resistance on its incoming branch. Loop resistance includes the return path; the model does not double it. Voltage is pole-to-pole/loop supply voltage, not an AC line-to-line or phase voltage. Units are source kV, node load kW, loop resistance Ω and branch current A.

There is no regeneration, voltage-dependent load, converter efficiency/dynamics, source droop/saturation, mesh, AC impedance/reactive power, capacitance, inductance, grounding or insulation model. All example values/criteria are fictional. Increasing voltage in this model is a sensitivity calculation, not equipment selection or a practical architecture recommendation.

## Iterative method

Start each load voltage at the source voltage. In deterministic parent-before-child order:

1. Calculate each local load current as P/V.
2. Sum downstream currents backward to obtain incoming branch currents.
3. Sweep forward: proposed child voltage = proposed parent voltage − branch current × loop resistance.
4. Dampen updates equally between old and proposed voltages.
5. Repeat, at most 500 iterations. Relative maximum update must be ≤ 10⁻¹⁰ of source voltage before residual checks.

A proposed voltage at or below 10⁻¹² of source voltage, or any nonfinite proposal, terminates the solve without metrics. Small updates alone do not pass: recompute branch currents and require the largest absolute voltage-equation residual ≤ source voltage × 10⁻⁸, and absolute energy-balance residual ≤ max(1 W, source power) × 10⁻⁷.

Voltage residual is `Vchild − Vparent + Ibranch R`. Energy balance is source power − sum(load power) − sum(Ibranch² R). Source current sums branches directly attached to the source. Source power is stiff-source voltage × source current. Line losses exclude every converter, transformer, switching, dielectric, cooling and auxiliary loss. Reported load/source efficiency is only this DC resistance model's ratio; it is null at zero source power.

## Solver states

`converged` means the numerical checks passed, not that a physical system is stable or safe. Constant-power networks can have multiple solutions; a flat-start fixed-point iteration generally targets the high-voltage branch where it converges, but is not a global existence, uniqueness or voltage-stability analysis.

`not-solved` withholds node rows and metrics and sets assessment to `not-assessed-solver-failure`. Reasons include iteration limit, a nonpositive/nonfinite iterate, or residual checks not met. Failure is not proof of physical infeasibility. No failed solve is turned into zero loss, acceptable voltage or passed criteria.

## Owner-declared criteria

Branch current is compared with max_current_a. Node voltage/source voltage is compared with min_voltage_fraction. Source power is compared with source_power_limit_mw when supplied. A null source criterion is unknown. Source criteria do not limit source behavior or shed load; they only flag an assumed solved demand exceeding the owner threshold.

Assessments are `declared-limit-violations`, `source-limit-unknown`, or `no-declared-limit-violations`. They are not manufacturer ratings, protection coordination, thermal limits, reliability predictions, compliance or safety approvals. Reliability notes are owner-authored context without a calculated failure-rate or availability model.

## Bounds and reproducibility

Up to 100 nodes and 20 scenarios. Loads and loop resistances are bounded to 10⁶ kW/Ω per node, source voltage 0.001–1000 kV, current criteria up to 10⁹ A and source-power criteria up to 10⁶ MW. These numerical bounds are software limits, not a validated physical domain. Model output remains educational even if input records include experimental measurements.

Web/Python parity is tested for normal, reordered, zero-load and failed-solve studies. Floating-point differences may affect close convergence/criterion boundaries. Bundle verification recomputes exact artifacts in the current runner; preserve Python version and runner revision for long-lived studies. Hashes are not signatures: replacement of all records and hashes can forge a self-consistent bundle.
