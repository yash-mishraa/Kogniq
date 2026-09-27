import asyncio
import os
import subprocess
import time
import uuid
import random
import sys

import httpx
import numpy as np

async def worker(client, stats, cookies, headers, is_instrumented=False):
    stats['actual_vus_started'] += 1
    
    for _ in range(5):
        stats['in_flight'] += 1
        stats['peak_in_flight'] = max(stats['peak_in_flight'], stats['in_flight'])
        start = time.perf_counter()
        
        choice = random.random()
        try:
            if choice < 0.7:
                req_type = "tutor"
                # If instrumented, we want to measure time taken by different parts.
                # Actually, from the client side, we can only measure HTTP request duration.
                # To measure server-side stuff (orchestration, LLM, DB), the server would need to return those in a header!
                # Since I need to "measure it", I can monkeypatch the server or just rely on server logs if I set them.
                # Wait, X-Process-Time-Ms is returned! But that's total.
                res = await client.post("/api/v1/agent/tutor/chat", json={"messages": [{"role": "user", "content": "Hello"}]}, cookies=cookies, headers=headers)
            elif choice < 0.9:
                req_type = "learning_hub"
                res = await client.post("/api/v1/retrieval/search", json={"query": "test", "limit": 5}, cookies=cookies, headers=headers)
            else:
                req_type = "ingestion"
                res = await client.post("/api/v1/documents/process", cookies=cookies, headers=headers, files={"file": ("test.txt", b"Hello", "text/plain")})
                
            dur = time.perf_counter() - start
            stats[f'req_{req_type}'] += 1
            stats[f'{req_type}_latencies'].append(dur)
            
            if res.status_code in (200, 202):
                stats[f'{req_type}_success'] += 1
                if is_instrumented and req_type == "tutor":
                    # Parse Server-Timing headers if we add them, else just store total
                    pass
            else:
                stats[f'{req_type}_error'] += 1
                stats['status_codes'][res.status_code] = stats['status_codes'].get(res.status_code, 0) + 1
        except Exception as e:
            dur = time.perf_counter() - start
            req_type = "tutor" if choice < 0.7 else ("learning_hub" if choice < 0.9 else "ingestion")
            stats[f'{req_type}_error'] += 1
            stats[f'{req_type}_latencies'].append(dur)
        finally:
            stats['in_flight'] -= 1
            stats['total_requests'] += 1
        await asyncio.sleep(0.1)

async def main(vus):
    env = os.environ.copy()
    env["KOGNIQ_API_ENVIRONMENT"] = "benchmark"
    env["PERSISTENCE_PROVIDER"] = "sqlite"
    db_path = os.path.abspath(f"test_db_{uuid.uuid4().hex}.sqlite")
    env["SQLITE_DATABASE_PATH"] = db_path
    
    proc = subprocess.Popen(
        ["uv", "run", "uvicorn", "apps.api.app.main:app", "--host", "127.0.0.1", "--port", "8099", "--workers", "1"],
        env=env,
        stdout=open(f"runner_{vus}_stdout.log", "w"),
        stderr=open(f"runner_{vus}_stderr.log", "w")
    )
    time.sleep(10)
    
    stats = {
        'actual_vus_started': 0,
        'in_flight': 0,
        'peak_in_flight': 0,
        'total_requests': 0,
        'req_tutor': 0,
        'req_learning_hub': 0,
        'req_ingestion': 0,
        'tutor_success': 0,
        'tutor_error': 0,
        'learning_hub_success': 0,
        'learning_hub_error': 0,
        'ingestion_success': 0,
        'ingestion_error': 0,
        'tutor_latencies': [],
        'learning_hub_latencies': [],
        'ingestion_latencies': [],
        'status_codes': {}
    }
    
    try:
        async with httpx.AsyncClient(base_url="http://127.0.0.1:8099", timeout=60.0, limits=httpx.Limits(max_connections=500)) as client:
            users = []
            print(f"Pre-authenticating {vus} benchmark users sequentially...")
            for i in range(vus):
                res = await client.post("/api/v1/auth/register", json={"email": f"vu_{i}_{uuid.uuid4().hex[:6]}@example.com", "password": "password", "display_name": f"VU {i}"})
                c = {"kogniq_session": res.cookies.get("kogniq_session")}
                h = {"Authorization": f"Bearer {c.get('kogniq_session', '')}"}
                users.append((c, h))
            
            print(f"Starting {vus}-VU Benchmark Runner...")
            start = time.perf_counter()
            tasks = [worker(client, stats, users[i][0], users[i][1], is_instrumented=(vus==100)) for i in range(vus)]
            await asyncio.gather(*tasks)
            dur = time.perf_counter() - start
            
            rps = stats['total_requests'] / dur if dur > 0 else 0
            
            def get_p(latencies, p):
                return np.percentile(latencies, p) * 1000 if latencies else 0
                
            print(f"\n--- {vus}-VU Benchmark Runner Metrics ---")
            print(f"Configured VUs: {vus}")
            print(f"Actual VUs Started: {stats['actual_vus_started']}")
            print(f"Total Requests: {stats['total_requests']}")
            print(f"Peak In-Flight Requests: {stats['peak_in_flight']}")
            print(f"Total Duration: {dur:.2f}s")
            print(f"Achieved RPS: {rps:.2f}")
            print(f"HTTP Status Distribution: {stats['status_codes']}")
            
            print("\n--- Tutor Workload ---")
            print(f"Requests: {stats['req_tutor']}")
            print(f"Success: {stats['tutor_success']}")
            print(f"Error: {stats['tutor_error']}")
            print(f"P50 Latency: {get_p(stats['tutor_latencies'], 50):.2f} ms")
            print(f"P95 Latency: {get_p(stats['tutor_latencies'], 95):.2f} ms")
            
            print("\n--- Learning Hub Workload ---")
            print(f"Requests: {stats['req_learning_hub']}")
            print(f"Success: {stats['learning_hub_success']}")
            print(f"Error: {stats['learning_hub_error']}")
            print(f"P50 Latency: {get_p(stats['learning_hub_latencies'], 50):.2f} ms")
            print(f"P95 Latency: {get_p(stats['learning_hub_latencies'], 95):.2f} ms")
            
            print("\n--- Ingestion Workload ---")
            print(f"Requests: {stats['req_ingestion']}")
            print(f"Success: {stats['ingestion_success']}")
            print(f"Error: {stats['ingestion_error']}")
            print(f"P50 Latency: {get_p(stats['ingestion_latencies'], 50):.2f} ms")
            print(f"P95 Latency: {get_p(stats['ingestion_latencies'], 95):.2f} ms")
            
    finally:
        proc.terminate()
        proc.wait()
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except:
                pass

if __name__ == '__main__':
    vus = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    asyncio.run(main(vus))
