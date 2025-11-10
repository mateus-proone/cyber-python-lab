#!/usr/bin/env python3
"""
network_monitor.py
Monitor simples de logs que detecta IPs com muitas falhas de login.
Uso: python3 blue_team/network_monitor.py logs/sample.log
"""

import sys
import re
from collections import Counter
from pathlib import Path
import time

IP_RE = re.compile(r'(\d{1,3}(?:\.\d{1,3}){3})')

def extract_ips(lines):
    ips = []
    for line in lines:
        m = IP_RE.search(line)
        if m:
            ips.append(m.group(1))
    return ips

def analyze(path, threshold=3):
    p = Path(path)
    if not p.exists():
        print(f"[ERROR] Arquivo não encontrado: {path}")
        return 1

    with p.open('r', encoding='utf-8', errors='ignore') as f:
        lines = [l.strip() for l in f if l.strip()]

    ips = extract_ips(lines)
    counts = Counter(ips)

    total = len(lines)
    unique = len(counts)
    print(f"[INFO] Linhas analisadas: {total} | IPs únicos: {unique}")

    alerts = [(ip, c) for ip, c in counts.most_common() if c >= threshold]
    if alerts:
        print(f"[ALERT] IPs com {threshold} ou mais ocorrências:")
        for ip, c in alerts:
            print(f" - {ip} : {c} ocorrências")
    else:
        print("[OK] Nenhum IP excedeu o limite.")

    return 0

def tail_mode(path, threshold=3, interval=5):
    # modo contínuo: verifica arquivo a cada interval segundos
    last_size = 0
    p = Path(path)
    print(f"[TAIL] Monitorando {path} (interval={interval}s) - use Ctrl+C para sair")
    try:
        while True:
            if p.exists():
                size = p.stat().st_size
                if size != last_size:
                    analyze(path, threshold=threshold)
                    last_size = size
            else:
                print(f"[WARN] Arquivo {path} não existe. Aguardando...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[STOP] Monitor interrompido pelo usuário.")

def usage():
    print("Uso: python3 blue_team/network_monitor.py <caminho_log> [threshold] [--tail]")
    print("  threshold: número mínimo de ocorrências para alerta (padrão 3)")
    print("  --tail : modo contínuo (verifica cada 5s)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    path = sys.argv[1]
    threshold = int(sys.argv[2]) if len(sys.argv) >= 3 and sys.argv[2].isdigit() else 3
    tail = '--tail' in sys.argv
    if tail:
        tail_mode(path, threshold=threshold, interval=5)
    else:
        sys.exit(analyze(path, threshold=threshold))
