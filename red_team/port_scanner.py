#!/usr/bin/env python3
"""
port_scanner.py
Scanner TCP simples e multi-thread.
Uso: python3 red_team/port_scanner.py <host> <start_port> <end_port> [threads]
Ex: python3 red_team/port_scanner.py 192.168.0.1 1 1024 100
**ATENÇÃO**: executar SOMENTE em hosts que você tem permissão (lab).
"""

import sys
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter

def scan_port(host, port, timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        return port, True
    except Exception:
        return port, False

def scan_range(host, start, end, workers=100):
    start_time = perf_counter()
    open_ports = []
    with ThreadPoolExecutor(max_workers=workers) as exe:
        futures = {exe.submit(scan_port, host, p): p for p in range(start, end+1)}
        for fut in as_completed(futures):
            p, open_ = fut.result()
            if open_:
                open_ports.append(p)
    end_time = perf_counter()
    return sorted(open_ports), end_time - start_time

def usage():
    print("Uso: python3 red_team/port_scanner.py <host> <start_port> <end_port> [threads]")
    print("Ex: python3 red_team/port_scanner.py 127.0.0.1 1 1024 200")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        usage()
        sys.exit(1)
    host = sys.argv[1]
    start_port = int(sys.argv[2])
    end_port = int(sys.argv[3])
    workers = int(sys.argv[4]) if len(sys.argv) >= 5 else 100

    print(f"[SCAN] Host: {host} Ports: {start_port}-{end_port} Threads: {workers}")
    open_ports, elapsed = scan_range(host, start_port, end_port, workers=workers)
    if open_ports:
        print("[RESULT] Open ports:", ", ".join(map(str, open_ports)))
    else:
        print("[RESULT] No open ports found in range.")
    print(f"[TIME] Elapsed: {elapsed:.2f}s")
