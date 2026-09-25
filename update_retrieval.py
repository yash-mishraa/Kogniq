import sys
import re

with open('packages/backend/src/backend/services/retrieval_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement_start = '''    async def search(self, request: RetrievalRequest) -> RetrievalResponse:
        start_time = time.perf_counter()
        scope = "document" if request.document_id else "global"
        logger.info(
            "retrieval_started",
            extra={
                "scope": scope
            }
        )
        warnings: list[str] = []'''

content = re.sub(r'    async def search\(self, request: RetrievalRequest\) -> RetrievalResponse:\n        start_time = time\.perf_counter\(\)\n        warnings: list\[str\] = \[\]', replacement_start, content, flags=re.DOTALL)

replacement_err1 = '''        except RetrievalError as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error("retrieval_failed", extra={"duration_ms": duration_ms, "status": "failure", "failure_category": "retrieval_error", "scope": scope})
            raise BackendError('''

content = re.sub(r'        except RetrievalError as e:\n            logger\.error\(f"Retriever error: {e}"\)\n            raise BackendError\(', replacement_err1, content, flags=re.DOTALL)

replacement_err2 = '''        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error("retrieval_failed", extra={"duration_ms": duration_ms, "status": "failure", "failure_category": "unknown_error", "scope": scope})
            raise BackendError('''

content = re.sub(r'        except Exception as e:\n            logger\.error\(f"Unexpected retrieval error: {e}"\)\n            raise BackendError\(', replacement_err2, content, flags=re.DOTALL)

replacement_end = '''        if len(results) > len(mapped_results) and len(mapped_results) < request.top_k:
            msg = "Results were found but filtered out (mismatch or threshold)."
            warnings.append(msg)

        end_time = time.perf_counter()
        processing_time_ms = (end_time - start_time) * 1000.0
        
        logger.info(
            "retrieval_completed",
            extra={
                "duration_ms": processing_time_ms,
                "result_count": len(mapped_results),
                "scope": scope,
                "status": "success",
            }
        )

        return RetrievalResponse('''

content = re.sub(r'        if len\(results\) > len\(mapped_results\) and len\(mapped_results\) < request\.top_k:.*?return RetrievalResponse\(', replacement_end, content, flags=re.DOTALL)

with open('packages/backend/src/backend/services/retrieval_service.py', 'w', encoding='utf-8') as f:
    f.write(content)
