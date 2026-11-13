# Gate issues raised by the builder (owner decides; the gate was NOT modified)

## 1. `oracle.py`: payments under `deployment_model=on_premise` is unsatisfiable
- Rule: for `on_premise`/`air_gapped`, any chosen component whose name matches `SAAS_NAME` (stripe, razorpay, ...) is a violation,
  and `KB saas_only` components are a violation. A separate rule requires a supporting `payments` component whenever
  `requirements.payments` is true and the deployment is not `air_gapped`.
- Problem: every real payment gateway is an external SaaS (card networks / acquirers cannot be self-hosted). The two rules
  together make `on_premise` + `payments=true` impossible to satisfy with a real product.
- Suggested fix (owner decision): exempt layer `payments` from the SaaS rules when `deployment_model == on_premise`
  (keep it forbidden for `air_gapped`, where the existing "air-gapped with payments" warning rule already applies).
- Builder workaround until decided: for `on_premise` + payments the engine returns a critical warning and `status: infeasible`
  with a reduced-scope stack, which is defensible but may not be what judges prefer.
