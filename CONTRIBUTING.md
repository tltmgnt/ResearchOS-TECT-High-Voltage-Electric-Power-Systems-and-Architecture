# Contributing

Run `node web/tests/model.test.mjs` and `python -m unittest discover -s tests -v`, plus the README workflow. Preserve graph validation, current/voltage/energy checks, failure/no-data semantics, units and web/Python parity. New models need domains, equations, independent reference checks and validation evidence.

Do not label convergence or owner-criterion checks as safety, reliability or equipment approval. Keep measured inputs distinct from educational output; do not change hashes or failed solver semantics to produce a green result. Protect credentials and unpublished partner data. Submit focused pull requests with behavior and verification evidence.
