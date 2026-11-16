# Primary source context

Reviewed November 16, 2026.

- [MATPOWER distribution power-flow manual](https://matpower.app/manual/matpower/DistributionPowerFlow.html): primary documentation describing radial backward/forward current summation and voltage sweeps in a broader AC context.
- [MATPOWER radial power-flow documentation](https://matpower.org/documentation/ref-manual/legacy/functions/radial_pf.html): reference context for radial solver methods.
- [DARPA Strategic Technology Office](https://www.darpa.mil/about/offices/sto) and [opportunities](https://www.darpa.mil/work-with-us/opportunities): research engagement context only. Check actual scope, instructions and amendments before any submission.

This repository independently implements an explicitly simplified real-valued DC variant from current summation and Ohm/Kirchhoff relationships. It does not include or claim equivalence to MATPOWER, an AC-grid model, a certified engineering tool or a complete high-voltage architecture analysis. No external solver package is required.

All example loads, voltages, resistances and criteria are fictional study inputs, not equipment ratings, DARPA requirements or practical design guidance. Sources establish context, not endorsement, novelty, safety or field performance.
