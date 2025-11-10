#!/usr/bin/env python3
"""
Versão com saída JSON e log simples.
Uso: python3 blue_team/network_monitor_json.py logs/sample.log
"""

import sys, os, re, json
from collections import Counter
from pathlib import Path
from datetime import datetime

IP_RE = re.compile(r'(\d{1,3}(?:\.\d{1,3}){3})')

def extract_ips(lines):
    return [m.group(1) for l in lines for m in [IP_RE.search(l)] if m]

def analyze(path, threshold=3, out_json=None):
    p = Path(path)
    if not p.exists():
        print(f"[ERROR] Arquivo não encontrado: {path}")
        return 1

    with p.open('r', encoding='utf-8', errors='ignore') as f:
        lines = [l.strip() for l in f if l.strip()]

    ips = extract_ips(lines)
    counts = Counter(ips)

    result = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "path": str(p),
        "lines": len(lines),
        "unique_ips": len(counts),
        "top": counts.most_common(10),
        "alerts": [(ip,c) for ip,c in counts.items() if c>=threshold]
    }

    print(json.dumps(result, indent=2))
    if out_json:
        with open(out_json, "w") as of:
            json.dump(result, of, indent=2)
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 blue_team/network_monitor_json.py <log> [threshold] [out.json]")
        sys.exit(1)
    path = sys.argv[1]
    threshold = int(sys.argv[2]) if len(sys.argv) >= 3 and sys.argv[2].isdigit() else 3
    out_json = sys.argv[3] if len(sys.argv) >= 4 else None
    sys.exit(analyze(path, threshold=threshold, out_json=out_json))
