import asyncio
import os
import subprocess
import time
import uuid
import random

import httpx
import numpy as np

async def worker(client, stats, cookies, headers):
    stats['actual_vus_started'] += 1
    
    for _ in range(5):
        stats['in_flight'] += 1
        stats['peak_in_flight'] = max(stats['peak_in_flight'], stats['in_flight'])
        start = time.perf_counter()
        
        choice = random.random()
        try:
            if choice < 0.7:
                req_type = "tutor"
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

async def main():
    env = os.environ.copy()
    env["KOGNIQ_API_ENVIRONMENT"] = "benchmark"
    env["PERSISTENCE_PROVIDER"] = "sqlite"
    db_path = os.path.abspath(f"test_db_{uuid.uuid4().hex}.sqlite")
    env["SQLITE_DATABASE_PATH"] = db_path
    
    proc = subprocess.Popen(
        ["uv", "run", "uvicorn", "apps.api.app.main:app", "--host", "127.0.0.1", "--port", "8099", "--workers", "1"],
        env=env,
        stdout=open("runner_stdout.log", "w"),
        stderr=open("runner_stderr.log", "w")
    )
    time.sleep(5)
    
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
        async with httpx.AsyncClient(base_url="http://127.0.0.1:8099", timeout=30.0, limits=httpx.Limits(max_connections=500)) as client:
            users = []
            print("Pre-authenticating 100 benchmark users sequentially to avoid initial lock contention...")
            for i in range(100):
                res = await client.post("/api/v1/auth/register", json={"email": f"vu_{i}_{uuid.uuid4().hex[:6]}@example.com", "password": "password", "display_name": f"VU {i}"})
                c = {"kogniq_session": res.cookies.get("kogniq_session")}
                h = {"Authorization": f"Bearer {c.get('kogniq_session', '')}"}
                users.append((c, h))
            
            print("Starting 100-VU Pre-release Smoke Runner...")
            start = time.perf_counter()
            tasks = [worker(client, stats, users[i][0], users[i][1]) for i in range(100)]
            await asyncio.gather(*tasks)
            dur = time.perf_counter() - start
            
            rps = stats['total_requests'] / dur if dur > 0 else 0
            
            def get_p(latencies, p):
                return np.percentile(latencies, p) * 1000 if latencies else 0
                
            print("--- 100-VU Pre-release Smoke Runner Metrics ---")
            print("Configured VUs: 100")
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
    asyncio.run(main())

