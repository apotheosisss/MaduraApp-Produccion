"""Mide tiempos de respuesta y rendimiento bajo concurrencia contra el backend
desplegado en AWS. Pensado para ejecutarse en un ambiente controlado.

Uso:  python medir_rendimiento.py [BASE_URL]
      (por defecto http://3.215.43.61:8000)
"""
import io
import json
import statistics as st
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import httpx
from PIL import Image

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://3.215.43.61:8000"
TIMEOUT = 30.0


def jpeg_bytes(color=(200, 180, 60)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (640, 640), color).save(buf, format="JPEG")
    return buf.getvalue()


def get_token() -> str:
    creds = {"username": "perftest", "email": "perf@maduraapp.cl", "password": "perftest123"}
    with httpx.Client(timeout=TIMEOUT) as c:
        r = c.post(f"{BASE}/v1/auth/register", json=creds)
        if r.status_code == 409:
            r = c.post(f"{BASE}/v1/auth/login",
                       json={"email": creds["email"], "password": creds["password"]})
        r.raise_for_status()
        return r.json()["access_token"]


def stats(samples_ms):
    samples_ms = sorted(samples_ms)
    n = len(samples_ms)
    p95 = samples_ms[min(n - 1, int(n * 0.95))]
    return {
        "n": n,
        "min_ms": round(min(samples_ms), 1),
        "avg_ms": round(st.mean(samples_ms), 1),
        "p95_ms": round(p95, 1),
        "max_ms": round(max(samples_ms), 1),
    }


def latency_seq(label, fn, n):
    samples, errors = [], 0
    for _ in range(n):
        t0 = time.perf_counter()
        try:
            fn()
            samples.append((time.perf_counter() - t0) * 1000)
        except Exception:
            errors += 1
    s = stats(samples) if samples else {"n": 0}
    s["errors"] = errors
    print(f"  {label}: {s}")
    return s


def concurrency(label, fn, concurrent, total):
    samples, errors = [], 0
    t_start = time.perf_counter()

    def one(_):
        t0 = time.perf_counter()
        try:
            fn()
            return (time.perf_counter() - t0) * 1000, True
        except Exception:
            return 0.0, False

    with ThreadPoolExecutor(max_workers=concurrent) as ex:
        for ms, ok in ex.map(one, range(total)):
            if ok:
                samples.append(ms)
            else:
                errors += 1
    wall = time.perf_counter() - t_start
    s = stats(samples) if samples else {"n": 0}
    s["errors"] = errors
    s["concurrent"] = concurrent
    s["throughput_rps"] = round(total / wall, 1) if wall else 0
    print(f"  {label} (c={concurrent}, n={total}): {s}")
    return s


def main():
    print(f"== Backend: {BASE} ==")
    token = get_token()
    hdr = {"Authorization": f"Bearer {token}"}
    img = jpeg_bytes()

    def call_health():
        with httpx.Client(timeout=TIMEOUT) as c:
            c.get(f"{BASE}/v1/health").raise_for_status()

    def call_predict():
        with httpx.Client(timeout=TIMEOUT) as c:
            c.post(f"{BASE}/v1/predict", headers=hdr,
                   files={"file": ("p.jpg", img, "image/jpeg")}).raise_for_status()

    out = {"base_url": BASE, "ts": time.strftime("%Y-%m-%d %H:%M:%S")}

    print("\n-- Tiempos de respuesta (secuencial) --")
    out["health_seq"] = latency_seq("/v1/health x30", call_health, 30)
    out["predict_seq"] = latency_seq("/v1/predict x15", call_predict, 15)

    print("\n-- Rendimiento bajo concurrencia --")
    out["health_conc"] = [concurrency("/v1/health", call_health, c, 40) for c in (5, 10, 20, 50)]
    out["predict_conc"] = [concurrency("/v1/predict", call_predict, c, 12) for c in (3, 6)]

    with open("perf_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("\nGuardado: perf_results.json")


if __name__ == "__main__":
    main()
