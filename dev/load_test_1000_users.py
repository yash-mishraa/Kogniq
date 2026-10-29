"""
Repeatable capacity benchmarking tool simulating concurrent API workers.
Measures throughput, latency percentiles (p50, p95, p99), error rates,
and system bottlenecks across realistic document intelligence operations.

Note on Topology: This script measures single-instance capacity against the local
Uvicorn / SQLite server. It measures actual demonstrated concurrency (e.g. 50-100 workers)
and isolates read-only vs retrieval workloads.
"""

import argparse
import asyncio
import json
import logging
import random
import statistics
import time
from typing import Any

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("load_test")


class LoadTester:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000/api/v1",
        concurrency: int = 100,
        total_requests: int = 500,
        workload: str = "mixed",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.concurrency = concurrency
        self.total_requests = total_requests
        self.workload = workload
        self.latencies: list[float] = []
        self.status_codes: dict[int, int] = {}
        self.errors: list[str] = []

    async def _login_demo_user(self, client: httpx.AsyncClient) -> str:
        try:
            resp = await client.post(
                f"{self.base_url}/auth/login",
                json={"email": "demo@kogniq.ai", "password": "Password123!"},
                headers={"X-Load-Test": "true"},
            )
            if resp.status_code == 200:
                cookie = resp.cookies.get("kogniq_session", "")
                return cookie
        except Exception:
            pass
        return ""

    async def _worker(
        self,
        worker_id: int,
        queue: asyncio.Queue[str],
        doc_ids: list[str],
        cookie: str = "",
    ) -> None:
        timeout = httpx.Timeout(15.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = {"X-User-Id": "demo-user-1", "X-Load-Test": "true"}
            if cookie:
                headers["Cookie"] = f"kogniq_session={cookie}"

            while not queue.empty():
                try:
                    op = await queue.get()
                except asyncio.QueueEmpty:
                    break

                doc_id = random.choice(doc_ids) if doc_ids else "test-doc"
                start = time.perf_counter()
                status_code = 0

                try:
                    if op == "documents_list":
                        resp = await client.get(f"{self.base_url}/documents", headers=headers)
                        status_code = resp.status_code
                    elif op == "system_overview":
                        resp = await client.get(f"{self.base_url}/system/overview", headers=headers)
                        status_code = resp.status_code
                    elif op == "system_ready":
                        resp = await client.get(f"{self.base_url}/system/ready", headers=headers)
                        status_code = resp.status_code
                    elif op == "knowledge_get":
                        resp = await client.get(f"{self.base_url}/knowledge/{doc_id}", headers=headers)
                        status_code = resp.status_code
                    elif op == "learning_get":
                        resp = await client.get(f"{self.base_url}/learning/{doc_id}", headers=headers)
                        status_code = resp.status_code
                    elif op == "retrieval_query":
                        resp = await client.post(
                            f"{self.base_url}/rag/retrieve",
                            json={
                                "query": "What is the transformer architecture and attention mechanism?",
                                "document_ids": [doc_id] if doc_id != "test-doc" else [],
                                "top_k": 3,
                                "minimum_similarity": 0.2,
                                "generate": False,
                            },
                            headers=headers,
                        )
                        status_code = resp.status_code
                    elif op == "rag_query":
                        resp = await client.post(
                            f"{self.base_url}/rag/query",
                            json={
                                "query": "Explain how multi-head attention works.",
                                "document_ids": [doc_id] if doc_id != "test-doc" else [],
                                "top_k": 2,
                                "minimum_similarity": 0.2,
                                "generate": True,
                            },
                            headers=headers,
                        )
                        status_code = resp.status_code
                    else:
                        resp = await client.get(f"{self.base_url}/version", headers=headers)
                        status_code = resp.status_code

                    elapsed = (time.perf_counter() - start) * 1000.0
                    self.latencies.append(elapsed)
                    self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
                except Exception as e:
                    elapsed = (time.perf_counter() - start) * 1000.0
                    self.latencies.append(elapsed)
                    self.errors.append(str(e))
                    self.status_codes[599] = self.status_codes.get(599, 0) + 1
                finally:
                    queue.task_done()

    async def run(self) -> dict[str, Any]:
        # 1. Fetch available documents & login once
        doc_ids: list[str] = []
        session_cookie = ""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                login_resp = await client.post(
                    f"{self.base_url}/auth/login",
                    json={"email": "demo@kogniq.ai", "password": "Password123!"},
                    headers={"X-Load-Test": "true"},
                )
                if login_resp.status_code == 200:
                    session_cookie = login_resp.cookies.get("kogniq_session", "")

                headers = {"X-User-Id": "demo-user-1", "X-Load-Test": "true"}
                if session_cookie:
                    headers["Cookie"] = f"kogniq_session={session_cookie}"

                resp = await client.get(f"{self.base_url}/documents", headers=headers)
                if resp.status_code == 200:
                    doc_ids = [d["id"] for d in resp.json()]
        except Exception as e:
            logger.warning(f"Setup error: {e}")

        # 2. Build workload queue
        queue: asyncio.Queue[str] = asyncio.Queue()
        if self.workload == "read_only":
            operations = (
                ["documents_list"] * 40
                + ["system_overview"] * 20
                + ["system_ready"] * 20
                + ["knowledge_get"] * 10
                + ["learning_get"] * 10
            )
        elif self.workload == "retrieval":
            operations = ["retrieval_query"]
        else:
            operations = (
                ["documents_list"] * 30
                + ["system_overview"] * 15
                + ["system_ready"] * 15
                + ["retrieval_query"] * 20
                + ["knowledge_get"] * 10
                + ["learning_get"] * 10
            )

        for _ in range(self.total_requests):
            queue.put_nowait(random.choice(operations))

        logger.info(
            f"Starting load test ({self.workload} workload): {self.total_requests} requests across {self.concurrency} concurrent workers"
        )
        start_time = time.perf_counter()

        timeout = httpx.Timeout(20.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as shared_client:
            headers = {"X-User-Id": "demo-user-1", "X-Load-Test": "true"}
            if session_cookie:
                headers["Cookie"] = f"kogniq_session={session_cookie}"

            async def _worker_shared():
                while not queue.empty():
                    try:
                        op = queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break

                    doc_id = random.choice(doc_ids) if doc_ids else "test-doc"
                    start = time.perf_counter()
                    status_code = 0
                    try:
                        if op == "documents_list":
                            resp = await shared_client.get(f"{self.base_url}/documents", headers=headers)
                        elif op == "system_overview":
                            resp = await shared_client.get(f"{self.base_url}/system/overview", headers=headers)
                        elif op == "system_ready":
                            resp = await shared_client.get(f"{self.base_url}/system/ready", headers=headers)
                        elif op == "knowledge_get":
                            resp = await shared_client.get(f"{self.base_url}/knowledge/{doc_id}", headers=headers)
                        elif op == "learning_get":
                            resp = await shared_client.get(f"{self.base_url}/learning/{doc_id}", headers=headers)
                        elif op == "retrieval_query":
                            resp = await shared_client.post(
                                f"{self.base_url}/rag/retrieve",
                                json={
                                    "query": "What is the transformer architecture and attention mechanism?",
                                    "document_ids": [doc_id] if doc_id != "test-doc" else [],
                                    "top_k": 3,
                                    "minimum_similarity": 0.2,
                                    "generate": False,
                                },
                                headers=headers,
                            )
                        else:
                            resp = await shared_client.get(f"{self.base_url}/version", headers=headers)
                        status_code = resp.status_code
                        elapsed = (time.perf_counter() - start) * 1000.0
                        self.latencies.append(elapsed)
                        self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
                    except Exception as exc:
                        elapsed = (time.perf_counter() - start) * 1000.0
                        self.latencies.append(elapsed)
                        self.errors.append(str(exc))
                        self.status_codes[599] = self.status_codes.get(599, 0) + 1
                    finally:
                        queue.task_done()

            workers = [
                asyncio.create_task(_worker_shared())
                for _ in range(min(self.concurrency, self.total_requests))
            ]
            await queue.join()
            for w in workers:
                w.cancel()

        total_duration = time.perf_counter() - start_time
        rps = len(self.latencies) / total_duration if total_duration > 0 else 0

        self.latencies.sort()
        count = len(self.latencies)
        p50 = self.latencies[int(count * 0.50)] if count else 0
        p90 = self.latencies[int(count * 0.90)] if count else 0
        p95 = self.latencies[int(count * 0.95)] if count else 0
        p99 = self.latencies[int(count * 0.99)] if count else 0

        results = {
            "target_concurrency": self.concurrency,
            "total_requests": count,
            "duration_seconds": round(total_duration, 2),
            "requests_per_second": round(rps, 2),
            "latency_ms": {
                "min": round(self.latencies[0], 2) if count else 0,
                "avg": round(statistics.mean(self.latencies), 2) if count else 0,
                "p50": round(p50, 2),
                "p90": round(p90, 2),
                "p95": round(p95, 2),
                "p99": round(p99, 2),
                "max": round(self.latencies[-1], 2) if count else 0,
            },
            "status_codes": self.status_codes,
            "error_count": len(self.errors),
        }

        logger.info("Load test completed.")
        logger.info(f"Throughput: {results['requests_per_second']} req/s")
        logger.info(f"Latency: p50={p50:.1f}ms, p95={p95:.1f}ms, p99={p99:.1f}ms")
        logger.info(f"Status codes: {self.status_codes}")
        return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kogniq capacity load testing tool")
    parser.add_argument("--url", default="http://127.0.0.1:8000/api/v1")
    parser.add_argument("--concurrency", type=int, default=100)
    parser.add_argument("--requests", type=int, default=500)
    parser.add_argument("--workload", choices=["mixed", "read_only", "retrieval"], default="mixed")
    args = parser.parse_args()

    tester = LoadTester(
        base_url=args.url,
        concurrency=args.concurrency,
        total_requests=args.requests,
        workload=args.workload,
    )
    res = asyncio.run(tester.run())
    print("\n" + json.dumps(res, indent=2))
