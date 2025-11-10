#!/usr/bin/env python3
"""
Scanner com banner grabbing simples.
Uso: python3 red_team/port_scanner_banner.py <host> <start> <end> [threads]
Resultado também salva em result.json
ATENÇÃO: execute apenas em lab.
"""
import sys, socket, json
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter

def scan_port(host, port, timeout=1.0):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        try:
            s.send(b'HEAD / HTTP/1.0\r\n\r\n')
            banner = s.recv(1024).decode(errors='ignore').strip()
        except Exception:
            banner = ""
        s.close()
        return port, True, banner
    except Exception:
        return port, False, ""

def scan_range(host, start, end, workers=100):
    start_time = perf_counter()
    open_ports = []
    with ThreadPoolExecutor(max_workers=workers) as exe:
        futures = {exe.submit(scan_port, host, p): p for p in range(start, end+1)}
        for fut in as_completed(futures):
            p, open_, banner = fut.result()
            if open_:
                open_ports.append({"port": p, "banner": banner})
    elapsed = perf_counter() - start_time
    return open_ports, elapsed

if __name__ == "__main__":
    if len(sys.argv)<4:
        print("Uso: python3 red_team/port_scanner_banner.py <host> <start> <end> [threads]")
        sys.exit(1)
    host = sys.argv[1]; s=int(sys.argv[2]); e=int(sys.argv[3])
    workers = int(sys.argv[4]) if len(sys.argv)>=5 else 100
    print(f"[SCAN] {host} {s}-{e} threads={workers}")
    results, elapsed = scan_range(host, s, e, workers)
    out = {"host": host, "range": f"{s}-{e}", "results": results, "time": elapsed}
    print(json.dumps(out, indent=2))
    with open("scan_result.json","w") as f:
        json.dump(out, f, indent=2)
    print(f"[SAVED] scan_result.json")
