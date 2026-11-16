"""Power-systems research records and strict JSON handling."""
import hashlib
import json
import math
import re
from pathlib import Path


class ValidationError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise ValidationError(message)


def dumps(value):
    return json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"


def parse_json(data):
    def constant(value):
        raise ValidationError(f"non-finite JSON constant: {value}")
    def unique(pairs):
        result = {}
        for k, v in pairs:
            require(k not in result, f"duplicate JSON key: {k}")
            result[k] = v
        return result
    return json.loads(data, parse_constant=constant, object_pairs_hook=unique)


def read_json(path):
    return parse_json(Path(path).read_text(encoding="utf-8"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text(v, name):
    require(isinstance(v, str) and bool(v.strip()), f"{name} must be a nonempty string")


def integer(v, name, minimum=0, maximum=10**12):
    require(type(v) is int and minimum <= v <= maximum, f"{name} must be an integer in [{minimum}, {maximum}]")


def number(v, name, positive=False):
    require(type(v) in (int, float), f"{name} must be numeric")
    try:
        finite = math.isfinite(v)
    except OverflowError:
        finite = False
    require(finite and (v > 0 if positive else v >= 0), f"{name} must be finite and {'positive' if positive else 'nonnegative'}")


def safe_path(value):
    text(value, "evidence path")
    require(not Path(value).is_absolute() and "\\" not in value and not re.match(r"^[A-Za-z]:", value)
            and not any(p in (".", "..") for p in value.split("/")), "evidence path must be relative without traversal")
    return Path(value)


def evidence_bytes(root, path):
    root = Path(root).resolve()
    dest = (root / safe_path(path)).resolve()
    require(dest.is_relative_to(root), "evidence resolves outside record directory")
    return dest.read_bytes()


def identifier(v,name):
    require(isinstance(v,str) and bool(re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}",v)),f"invalid {name}")


def node_order(nodes):
    remaining={n["id"]:n["parent"] for n in nodes};done={"source"};order=[]
    while remaining:
        ready=sorted(k for k,p in remaining.items() if p in done)
        require(bool(ready),"network contains a cycle or disconnected parent chain")
        for k in ready:
            order.append(k);done.add(k);del remaining[k]
    return order


def validate(r):
    require(isinstance(r,dict),"record must be an object")
    require(type(r.get("schema_version")) is int and r["schema_version"]==1,"schema_version must be integer 1")
    identifier(r.get("id"),"record id")
    for k in ("title","owner","hypothesis","protocol_reference","differentiation","reliability_notes"):
        text(r.get(k),k)
    require(r.get("data_kind") in ("synthetic","simulation","experimental"),"invalid input basis")
    nodes=r.get("nodes")
    require(isinstance(nodes,list) and 1<=len(nodes)<=100,"provide 1–100 load nodes")
    ids=set()
    for n in nodes:
        require(isinstance(n,dict),"node must be an object")
        identifier(n.get("id"),"node id");require(n["id"]!="source" and n["id"] not in ids,"duplicate/reserved node id");ids.add(n["id"])
        text(n.get("label"),"node label");text(n.get("parent"),"parent")
        for key in ("load_kw","line_resistance_ohm"):
            number(n.get(key),key);require(n[key]<=1e6,f"{key} must be <=1e6")
        number(n.get("max_current_a"),"max_current_a",True);require(n["max_current_a"]<=1e9,"current criterion must be <=1e9 A")
        number(n.get("min_voltage_fraction"),"min_voltage_fraction",True);require(n["min_voltage_fraction"]<=1,"minimum voltage fraction must be <=1")
    for n in nodes:
        require(n["parent"] in ids|{"source"} and n["parent"]!=n["id"],"unknown/self parent")
    node_order(nodes)
    scenarios=r.get("scenarios")
    require(isinstance(scenarios,list) and 1<=len(scenarios)<=20,"provide 1–20 scenarios")
    seen=set()
    for s in scenarios:
        require(isinstance(s,dict),"scenario must be an object")
        identifier(s.get("id"),"scenario id");require(s["id"] not in seen,"duplicate scenario id");seen.add(s["id"])
        for k in ("label","assumption_reference"):
            text(s.get(k),k)
        number(s.get("source_voltage_kv"),"source_voltage_kv",True);require(.001<=s["source_voltage_kv"]<=1000,"source voltage must be 0.001–1000 kV")
        if s.get("source_power_limit_mw") is not None:
            number(s["source_power_limit_mw"],"source_power_limit_mw",True);require(s["source_power_limit_mw"]<=1e6,"source power criterion must be <=1e6 MW")
    evidence=r.get("evidence");require(isinstance(evidence,list),"evidence must be an array");refs,paths=set(),set()
    for e in evidence:
        require(isinstance(e,dict),"evidence entry must be an object")
        for k in ("id","description"):
            text(e.get(k),k)
        safe_path(e.get("path"));require(e["id"] not in refs and e["path"] not in paths,"duplicate evidence id/path");refs.add(e["id"]);paths.add(e["path"])
        require(isinstance(e.get("sha256"),str) and bool(re.fullmatch(r"[a-f0-9]{64}",e["sha256"])),"invalid evidence digest")
    measurements=r.get("measurements");require(isinstance(measurements,list),"measurements must be an array")
    for m in measurements:
        require(isinstance(m,dict),"measurement must be an object")
        for k in ("metric","unit","method"):
            text(m.get(k),k)
        value=m.get("value");require(type(value) in (int,float) and -1e15<=value<=1e15,"measurement value must be finite within +/-1e15")
        number(m.get("uncertainty"),"measurement uncertainty")
        links=m.get("evidence_ids");require(isinstance(links,list) and all(isinstance(x,str) and x in refs for x in links),"unknown measurement evidence reference")
        require(r["data_kind"]!="experimental" or bool(links),"experimental measurements require evidence references")
    require(r["data_kind"]!="experimental" or bool(evidence) and bool(measurements),"experimental records require measurements and evidence")
    return r
