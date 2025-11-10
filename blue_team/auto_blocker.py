#!/usr/bin/env python3
"""
auto_blocker.py
Leitura segura de artifacts/output.json e atualização de shared/blocklist.txt (simulado).
Uso: python3 blue_team/auto_blocker.py artifacts/output.json
Saída: shared/blocklist.txt (adiciona IPs únicos) e artifacts/block_actions.log (registro)
"""
import sys, json, os
from pathlib import Path
from datetime import datetime

def load_alert_ips(json_path):
    p = Path(json_path)
    if not p.exists():
        print(f"[ERROR] arquivo não encontrado: {json_path}")
        return []
    data = json.loads(p.read_text(encoding='utf-8'))
    # data['alerts'] expected as list of [ip, count] or list of tuples
    alerts = data.get("alerts", [])
    ips = []
    for item in alerts:
        if isinstance(item, list) or isinstance(item, tuple):
            ips.append(item[0])
        elif isinstance(item, str):
            ips.append(item)
        elif isinstance(item, dict):
            # fallback if someone changed format
            ip = item.get("ip") or item.get("address")
            if ip:
                ips.append(ip)
    # normalize unique and simple validation
    uniq = []
    for ip in ips:
        ip = ip.strip()
        if ip and ip not in uniq:
            uniq.append(ip)
    return uniq

def ensure_shared():
    p = Path("shared")
    p.mkdir(exist_ok=True)
    bl = p / "blocklist.txt"
    if not bl.exists():
        bl.write_text("", encoding='utf-8')
    return bl

def add_to_blocklist(blockfile, ips):
    existing = set()
    text = blockfile.read_text(encoding='utf-8')
    for line in text.splitlines():
        line = line.strip()
        if line:
            existing.add(line)
    new_added = []
    for ip in ips:
        if ip not in existing:
            existing.add(ip)
            new_added.append(ip)
    # overwrite file with sorted list
    blockfile.write_text("\n".join(sorted(existing)) + ("\n" if existing else ""), encoding='utf-8')
    return new_added

def log_actions(added_ips, src_json):
    p = Path("artifacts")
    p.mkdir(exist_ok=True)
    lf = p / "block_actions.log"
    ts = datetime.utcnow().isoformat() + "Z"
    with lf.open("a", encoding='utf-8') as f:
        for ip in added_ips:
            f.write(f"{ts} ADDED {ip} from {src_json}\n")

def usage():
    print("Uso: python3 blue_team/auto_blocker.py <artifacts/output.json>")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage(); sys.exit(1)
    src = sys.argv[1]
    ips = load_alert_ips(src)
    if not ips:
        print("[INFO] Nenhum IP em alerts para processar.")
        sys.exit(0)
    blockfile = ensure_shared()
    new = add_to_blocklist(blockfile, ips)
    if new:
        log_actions(new, src)
        print(f"[OK] Adicionados {len(new)} IP(s) ao {blockfile}")
    else:
        print("[OK] Nenhum IP novo para adicionar.")
