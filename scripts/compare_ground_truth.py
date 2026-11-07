#!/usr/bin/env python3
"""Compare OSV-Scanner and Grype JSON against manually verified ground truth.

Only CSV rows marked 'verified' are scored. Unlisted findings are unadjudicated,
not false positives, because the ground-truth corpus may be incomplete.
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
    expected=defaultdict(set)
    with open(args.ground_truth, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("status","").strip().lower() != "verified":
                continue
            expected[row["project_id"]].add((norm(row["package"]), row["version"].strip(), norm(row["vulnerability_id"])))
    rows=[]
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        meta=read_json(folder/"project.json")
        project_id=meta.get("project_id", folder.name.split("-")[0])
        exp=expected.get(project_id, set())
        for tool, filename, parser in (
            ("OSV-Scanner","osv-result.json",osv_findings),
            ("Grype","grype-result.json",grype_findings),
        ):
            actual=parser(read_json(folder/filename))
            tp=exp & actual
            fn=exp - actual
            unadjudicated=actual - exp
            recall=(len(tp)/len(exp)) if exp else None
            rows.append({
                "project_id":project_id, "project":meta.get("name",""),
                "tool":tool, "verified_expected":len(exp), "true_positives":len(tp),
                "false_negatives":len(fn), "unadjudicated_findings":len(unadjudicated),
                "recall":round(recall,4) if recall is not None else "",
                "scoring_status":"scored" if exp else "no_verified_ground_truth"
            })
    with open(out/"comparison.csv","w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ["project_id","project","tool","verified_expected","true_positives","false_negatives","unadjudicated_findings","recall","scoring_status"])
        writer.writeheader(); writer.writerows(rows)
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
