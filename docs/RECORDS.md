# Study record contract v1

The executable validator is `researchos_power/records.py`. Duplicate JSON keys, NaN and Infinity are rejected. Booleans cannot replace numeric fields. Unknown metadata is retained. IDs are 1–80 lowercase letters/digits/underscores/hyphens, starting alphanumeric.

| Field | Contract |
| --- | --- |
| schema_version | Integer 1 |
| id | Safe study ID |
| title, owner, hypothesis | Nonempty strings |
| protocol_reference, differentiation, reliability_notes | Nonempty protocol, research-distinction and reliability-gap notes |
| data_kind | synthetic, simulation or experimental; describes inputs |
| nodes | 1–100 load-node objects |
| scenarios | 1–20 source-scenario objects |
| measurements | Array, possibly empty for nonexperimental inputs |
| evidence | Array of evidence declarations |

Each node requires unique safe id (excluding reserved `source`), label, parent, load_kw, line_resistance_ohm, max_current_a and min_voltage_fraction. Parent must be `source` or another existing node, never self. Cycles/disconnected parent chains fail. Load and resistance are finite nonnegative values; branch-current criterion is positive; minimum voltage fraction is in (0,1]. See model bounds. Removing/renaming nodes requires updating parent references.

Each scenario requires unique safe id, label, positive source_voltage_kv, null or positive source_power_limit_mw, and nonempty assumption_reference. Criteria are owner inputs, not validated equipment limits.

Every measurement has nonempty metric/unit/method, finite value in ±10¹⁵, finite nonnegative uncertainty and evidence_ids referencing declared evidence. State calibration, acquisition conditions, coverage/confidence and uncertainty interpretation in method/metadata. Experimental records require at least one measurement and evidence file, with references on each measurement. The solver does not fit or validate measurements or propagate uncertainty.

Each evidence declaration has unique nonempty id, unique relative path, lowercase 64-character sha256 and nonempty description. Use `researchos-power hash <file>`. Absolute/drive paths, traversal and symlinks outside the record directory are rejected. Verified bytes are captured under generated filenames mapped to original evidence IDs in the manifest.

The CLI refuses to overwrite existing run directories. Verification checks hashes, evidence-to-record consistency and reproduction of results/report/node CSV. Original source evidence may be moved after capture because the bundle retains its bytes. Web exports are summaries and study JSON, not complete CLI evidence bundles.
