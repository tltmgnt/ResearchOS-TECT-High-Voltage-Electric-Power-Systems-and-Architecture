# ResearchOS TECT — High-Voltage Electric Power Systems and Architecture

Independent research workspace for high-voltage electric power systems and architecture, supporting reproducible modeling, architecture comparisons, power-flow and loss analysis, experiment design, and evidence-linked assessment of performance, reliability, uncertainty, and research differentiation.

## Implemented foundation

- Educational steady-state radial DC power flow with one stiff source and nonnegative constant-power loads.
- Damped backward/forward sweep, current summation, voltage-equation and energy-balance residual checks.
- Source-voltage architecture scenarios with branch currents, node voltages, resistance losses and owner-declared criteria.
- Explicit failed-solve states that withhold metrics/assessments; unknown source criteria remain unknown.
- Strict records, reliability/differentiation notes, signed declared measurements with uncertainty, evidence hashes and portable verified bundles.
- A local-first browser app with node/scenario editing, logical topology, loss comparisons, per-scenario inspection, evidence checks and JSON/CSV/Markdown exports.

This is a research software foundation, not a validated high-voltage design tool. No AC-grid power flow, converter dynamics, insulation coordination, grounding, protection, fault/arc analysis, thermal assessment, switching transient, stability, reliability prediction or hardware control is implemented. Convergence and no declared violations do not establish safety, operability, reliability or engineering approval. No DARPA affiliation, award, endorsement, eligibility, submission or novel architecture is claimed. TECT remains the project identifier without an assumed expansion.

## Quick start

Python 3.10 or newer; no third-party runtime dependencies:

```bash
python -m researchos_power validate examples/synthetic-power.json
python -m researchos_power run examples/synthetic-power.json --output runs/demo
python -m researchos_power verify runs/demo
python -m researchos_power report runs/demo
python -m unittest discover -s tests -v
```

Optional installation:

```bash
python -m pip install .
researchos-power --help
```

The synthetic fixture serves 5 MW of constant-power loads. At the fictional 100 kV source, modeled line losses are approximately 6.71885 kW and one branch exceeds its owner-declared current criterion. At 200 kV, modeled line losses are approximately 1.67617 kW and no declared criteria are exceeded. A third scenario intentionally violates its source-power criterion. These are arithmetic studies with fictional values, not equipment ratings or an operating-system recommendation.

## Browser app

Serve `web/` with `python -m http.server 8000 --directory web`, then open `http://localhost:8000`. Use localhost or HTTPS for modules, workers and Web Crypto. Run web-model tests with `node web/tests/model.test.mjs`.

Calculations run in a worker. Records remain in the current browser and origin; export regularly. No cross-device, GitHub or CLI synchronization is configured. Study JSON exports work with the CLI; browser result/report exports are summaries, not full CLI evidence bundles. Files are hashed locally, never uploaded or retained; original evidence must be preserved separately. Imported/reloaded records do not re-verify it.

The form creates synthetic/simulation records. Experimental records can be imported with measurements/evidence declarations; model outputs remain educational. Reusing parameters as a new record changes experimental basis to simulation and omits original measurements/evidence, leaving the original saved record intact. Browser logical topology is not a wiring or construction diagram.

## Research workflow

1. Copy the example; assign a unique ID, owner, hypothesis, protocol reference and honest input basis.
2. Define a radial tree of load nodes. Each parent is `source` or another node ID. Resistance is total DC loop resistance, including the return path.
3. Define stiff-source voltage scenarios and optional source-power criteria. Node voltage/current criteria are owner research inputs, not independently validated equipment limits.
4. Document reliability gaps, proposed differentiation and related-work review. The solver does not predict availability or certify novelty.
5. Add declared measurements with method, units, uncertainty and evidence IDs. These values are retained separately without fitting or validation.
6. Place evidence below the record directory; use `researchos-power hash <file>` and declare its relative path, digest, description and ID.
7. Validate, run into a new directory, verify, and review all assumptions, failures and residuals. Existing run directories are rejected.

Experimental records require measurements and evidence references. Paths cannot escape the record directory, including through symlinks. Verified evidence bytes are captured. Hashes establish byte consistency, not authenticity, calibration or engineering validity. Local bundles are ignored by Git; keep unpublished partner data and credentials out of this public repository.

## Bundle contents

| File | Purpose |
| --- | --- |
| `record.json` | Exact original study bytes |
| `results.json` | Scenario solver states, node results, metrics, owner criteria and limitations |
| `nodes.csv` | Per-scenario node rows; unsolved scenarios have explicit status rows without metrics |
| `report.md` | Scenario summary, reliability and differentiation notes |
| `evidence/0000.bin`, … | Captured original evidence bytes |
| `manifest.json` | File digests, evidence mapping and Python version |

Verification checks hashes, evidence-to-record consistency and recomputes results/report/CSV. Identical input/runtime produces identical bundles. These are ordinary files, not a signed or tamper-proof audit service.

## Documentation and CI

- [Equations and solver limits](docs/MODEL.md)
- [Record contract](docs/RECORDS.md)
- [Research roadmap](docs/RESEARCH_PLAN.md)
- [Primary source context](docs/SOURCES.md)
- [Contributing](CONTRIBUTING.md)

CI runs JavaScript checks, web tests, Python tests, full web/Python parity, installed CLI execution and synthetic bundle uploads across Python 3.10–3.13. The existing [license](LICENSE) is preserved.

Private hosted app: https://researchos-tect-power-systems.troturn31.chatgpt.site
