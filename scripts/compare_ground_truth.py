#!/usr/bin/env python3
"""Compare OSV-Scanner and Grype JSON against manually verified ground truth.

A ground-truth row may list multiple equivalent advisory identifiers (for example
GHSA and CVE). It counts as one expected vulnerability, matched by any alias.
Only rows marked 'verified' are scored.
"""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from collections import defaultdict

def norm(value: object) -> str:
    return str(value or "").strip().lower().replace("_", "-")

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

def osv_findings(data):
    found=set()
    for result in data.get("results", []) or []:
        for pkg in result.get("packages", []) or []:
            p = pkg.get("package", {}) or {}
            name = norm(p.get("name"))
            version = str(p.get("version") or "")
            for vuln in pkg.get("vulnerabilities", []) or []:
                found.add((name, version, norm(vuln.get("id"))))
    return found

def grype_findings(data):
    found=set()
    for match in data.get("matches", []) or []:
        artifact = match.get("artifact", {}) or {}
        vuln = match.get("vulnerability", {}) or {}
        found.add((norm(artifact.get("name")), str(artifact.get("version") or ""), norm(vuln.get("id"))))
    return found

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--results-dir", required=True)
    ap.add_argument("--ground-truth", required=True)
    ap.add_argument("--output-dir", required=True)
    args=ap.parse_args()
    root=Path(args.results_dir); out=Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    expected=defaultdict(list)
    with open(args.ground_truth, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("status","").strip().lower() != "verified":
                continue
            ids=row.get("vulnerability_ids") or row.get("vulnerability_id","")
            aliases={norm(x) for x in ids.replace(",", ";").split(";") if x.strip()}
            expected[row["project_id"]].append((norm(row["package"]), row["version"].strip(), aliases))
    rows=[]
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        meta=read_json(folder/"project.json")
        project_id=meta.get("project_id", folder.name.split("-")[0])
        exp=expected.get(project_id, [])
        for tool, filename, parser in (
            ("OSV-Scanner","osv-result.json",osv_findings),
            ("Grype","grype-result.json",grype_findings),
        ):
            actual=parser(read_json(folder/filename))
            matched=set()
            for package, version, aliases in exp:
                if any((package, version, alias) in actual for alias in aliases):
                    matched.add((package, version, tuple(sorted(aliases))))
            tp=len(matched)
            fn=len(exp)-tp
            adjudicated_actual=set()
            for package, version, aliases in exp:
                adjudicated_actual.update((package, version, alias) for alias in aliases)
            unadjudicated=actual-adjudicated_actual
            recall=(tp/len(exp)) if exp else None
            rows.append({
                "project_id":project_id, "project":meta.get("name",""),
                "tool":tool, "verified_expected":len(exp), "true_positives":tp,
                "false_negatives":fn, "unadjudicated_findings":len(unadjudicated),
                "recall":round(recall,4) if recall is not None else "",
                "scoring_status":"scored" if exp else "no_verified_ground_truth"
            })
    fields=["project_id","project","tool","verified_expected","true_positives","false_negatives","unadjudicated_findings","recall","scoring_status"]
    with open(out/"comparison.csv","w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    (out/"comparison.json").write_text(json.dumps(rows,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    summary={}
    for tool in ("OSV-Scanner","Grype"):
        rs=[r for r in rows if r["tool"]==tool and r["scoring_status"]=="scored"]
        total=sum(r["verified_expected"] for r in rs); tp=sum(r["true_positives"] for r in rs)
        summary[tool]={"verified_expected":total,"true_positives":tp,"false_negatives":total-tp,
                       "recall":round(tp/total,4) if total else None,
                       "note":"Unadjudicated findings are not counted as false positives."}
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
