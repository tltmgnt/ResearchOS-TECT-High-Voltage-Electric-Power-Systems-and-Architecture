"""Damped backward/forward DC constant-power flow on a radial tree."""
import math
from .records import dumps,node_order,validate
LIMITATIONS=("Educational steady-state DC models only. One stiff source, radial resistive loop paths and nonnegative constant-power loads are assumed. Declared current/voltage/source criteria are owner inputs, not equipment ratings or safety approvals. No AC power flow, converter dynamics, insulation coordination, grounding, protection, fault/arc analysis, thermal limits, transient stability, reliability prediction or hardware integration is implemented. Convergence and limit checks do not establish an operable or safe high-voltage design, novelty or DARPA compliance.")


def solve(nodes,scenario,max_iterations=500):
    order=node_order(nodes);lookup={n["id"]:n for n in nodes};source=scenario["source_voltage_kv"]*1000
    voltage={key:source for key in order};load=sum(n["load_kw"]*1000 for n in nodes)
    def currents(v):
        branch={key:lookup[key]["load_kw"]*1000/v[key] for key in order}
        for key in reversed(order):
            parent=lookup[key]["parent"]
            if parent!="source":branch[parent]+=branch[key]
        return branch
    failure="iteration-limit";iterations=0
    for iterations in range(1,max_iterations+1):
        branch=currents(voltage);proposal={"source":source}
        for key in order:
            n=lookup[key];proposal[key]=proposal[n["parent"]]-branch[key]*n["line_resistance_ohm"]
        if any(not math.isfinite(proposal[k]) or proposal[k]<=source*1e-12 for k in order):
            failure="nonpositive-or-nonfinite-voltage-iterate";break
        updated={key:.5*voltage[key]+.5*proposal[key] for key in order}
        change=max(abs(updated[k]-voltage[k])/source for k in order);voltage=updated
        if change<=1e-10:
            branch=currents(voltage)
            residual=max(abs(voltage[k]-(source if lookup[k]["parent"]=="source" else voltage[lookup[k]["parent"]])+branch[k]*lookup[k]["line_resistance_ohm"]) for k in order)
            source_current=sum(branch[k] for k in order if lookup[k]["parent"]=="source")
            source_power=source*source_current;loss=sum(branch[k]**2*lookup[k]["line_resistance_ohm"] for k in order)
            energy=source_power-load-loss
            if residual<=source*1e-8 and abs(energy)<=max(1,source_power)*1e-7:
                rows=[];violations=[]
                for key in order:
                    n=lookup[key];current_met=branch[key]<=n["max_current_a"];voltage_met=voltage[key]/source>=n["min_voltage_fraction"]
                    if not current_met:violations.append(key+":current")
                    if not voltage_met:violations.append(key+":voltage")
                    rows.append({"node_id":key,"voltage_kv":voltage[key]/1000,"voltage_fraction":voltage[key]/source,
                                 "branch_current_a":branch[key],"line_loss_kw":branch[key]**2*n["line_resistance_ohm"]/1000,
                                 "load_kw":n["load_kw"],"declared_current_met":current_met,"declared_voltage_met":voltage_met})
                cap=scenario.get("source_power_limit_mw");source_met=source_power/1e6<=cap if cap is not None else None
                if source_met is False:violations.append("source:power")
                return {"scenario_id":scenario["id"],"status":"converged","iterations":iterations,"failure_reason":None,
                        "source_voltage_kv":scenario["source_voltage_kv"],"node_results":rows,
                        "metrics":{"total_load_mw":load/1e6,"source_power_mw":source_power/1e6,"line_losses_kw":loss/1000,
                                   "efficiency_fraction":load/source_power if source_power else None,"source_current_a":source_current,
                                   "energy_balance_residual_w":energy,"max_voltage_equation_residual_v":residual},
                        "declared_source_limit_met":source_met,"declared_limit_violations":violations,
                        "assessment":"declared-limit-violations" if violations else ("source-limit-unknown" if source_met is None else "no-declared-limit-violations")}
            failure="residual-checks-not-met"
    return {"scenario_id":scenario["id"],"status":"not-solved","iterations":iterations,"failure_reason":failure,
            "source_voltage_kv":scenario["source_voltage_kv"],"node_results":[],"metrics":None,
            "declared_source_limit_met":None,"declared_limit_violations":[],"assessment":"not-assessed-solver-failure"}


def analyze(record):
    r=validate(record);result={"analysis":"radial-dc-constant-power-v1","runner_version":"0.1.0","input_data_kind":r["data_kind"],
                            "output_kind":"educational-dc-study","scenario_results":[solve(r["nodes"],s) for s in r["scenarios"]],
                            "reliability_notes":r["reliability_notes"],"declared_measurements":r["measurements"],"limitations":LIMITATIONS}
    dumps(result);return result
