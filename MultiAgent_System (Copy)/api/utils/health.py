# healthchecks.py
import os
import time
import asyncio
from typing import Any, Dict, Optional

import asyncpg
import aiohttp
from yarl import URL

def result(name: str, ok: bool, start: float, detail: Optional[Dict[str, Any]] = None):
    return {
        "service": name,
        "ok": ok,
        "latency_ms": round((time.perf_counter() - start) * 1000, 1),
        "detail": detail or {},
    }


# async def check_postgres(
#     dsn: Optional[str] = None,
#     host: str = "localhost",
#     port: int = 5432,
#     user: str = "postgres",
#     password: str = "",
#     database: str = "postgres",
#     connect_timeout: float = 2.0,  # giây
# ) -> Dict[str, Any]:
#
#     start = time.perf_counter()
#     try:
#         if dsn:
#             conn = await asyncpg.connect(dsn=dsn, timeout=connect_timeout)
#         else:
#             conn = await asyncpg.connect(
#                 host=host,
#                 port=port,
#                 user=user,
#                 password=password,
#                 database=database,
#                 timeout=connect_timeout,
#             )
#         try:
#             val = await conn.fetchval("SELECT 1;")
#             return result("postgresql", val == 1, start, {"db": database})
#         finally:
#             await conn.close()
#     except Exception as e:
#         return result("postgresql", False, start, {"error": str(e)})


async def check_qdrant(
    base_url: str = "http://localhost:6333",
    api_key: Optional[str] = None,
    endpoint: str = "/readyz",
    timeout: float = 2.0,
) -> Dict[str, Any]:

    start = time.perf_counter()
    url = str(URL(base_url) / endpoint.lstrip("/"))
    headers = {}

    if api_key:
        headers["api-key"] = api_key

    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url, headers=headers, timeout=timeout) as resp:
                ok = resp.status == 200
                text = await resp.text()
                return result("qdrant", ok, start, {"status": resp.status, "body": text[:200]})
    except Exception as e:
        return result("qdrant", False, start, {"error": str(e), "url": url})

# async def check_elasticsearch(
#     base_url: str = "http://localhost:9200",
#     username: Optional[str] = None,
#     password: Optional[str] = None,
#     api_key: Optional[str] = None,
#     timeout: float = 2.5,
# ) -> Dict[str, Any]:
#
#     start = time.perf_counter()
#     url = str(URL(base_url) / "_cluster" / "health")
#     headers = {}
#     auth = None
#     if api_key:
#         headers["Authorization"] = f"ApiKey {api_key}"
#     elif username and password:
#         auth = aiohttp.BasicAuth(username, password)
#
#     try:
#         async with aiohttp.ClientSession() as sess:
#             async with sess.get(url, headers=headers, auth=auth, timeout=timeout) as resp:
#                 data = await resp.json(loads=None, content_type=None)
#                 status = data.get("status")
#                 ok = resp.status == 200 and status in {"green", "yellow"}  # đỏ coi như fail
#                 return result("elasticsearch", ok, start, {"http": resp.status, "status": status})
#     except Exception as e:
#         return result("elasticsearch", False, start, {"error": str(e), "url": url})

async def check_minio(
    base_url: str = "http://localhost:9000",
    endpoint: str = "/minio/health/ready",
    timeout: float = 2.0,
) -> Dict[str, Any]:

    start = time.perf_counter()
    url = str(URL(base_url) / endpoint.lstrip("/"))
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url, timeout=timeout) as resp:
                ok = resp.status == 200
                return result("minio", ok, start, {"status": resp.status})
    except Exception as e:
        return result("minio", False, start, {"error": str(e), "url": url})


# async def check_all() -> Dict[str, Any]:
#     tasks = [
#         check_postgres(
#             host=os.getenv("POSTGRES_HOST", "localhost"),
#             port=int(os.getenv("POSTGRES_POST", "5432")),
#             user=os.getenv("POSTGRES_USER", "postgres"),
#             password=os.getenv("POSTGRES_PASSWORD", ""),
#             database=os.getenv("POSTGRES_DB", "postgres"),
#             connect_timeout=float(os.getenv("PG_CONNECT_TIMEOUT", "2.0")),
#         ),
#         check_qdrant(
#             base_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
#             api_key=os.getenv("QDRANT_API_KEY"),
#             endpoint=os.getenv("QDRANT_ENDPOINT", "/readyz"),
#             timeout=float(os.getenv("QDRANT_TIMEOUT", "2.0")),
#         ),
#         check_elasticsearch(
#             base_url=os.getenv("ES_URL", "http://localhost:9200"),
#             username=os.getenv("ES_USERNAME"),
#             password=os.getenv("ES_PASSWORD"),
#             api_key=os.getenv("ES_API_KEY"),
#             timeout=float(os.getenv("ES_TIMEOUT", "2.5")),
#         ),
#         check_minio(
#             base_url=os.getenv("MINIO_URL", "http://localhost:9000"),
#             endpoint=os.getenv("MINIO_ENDPOINT", "/minio/health/ready"),
#             timeout=float(os.getenv("MINIO_TIMEOUT", "2.0")),
#         ),
#     ]
#     results = await asyncio.gather(*tasks, return_exceptions=False)
#     overall_ok = all(r["ok"] for r in results)
#     return {"ok": overall_ok, "services": results}
#
# if __name__ == "__main__":
#     out = asyncio.run(check_all())
#     import json
#     print(json.dumps(out, ensure_ascii=False, indent=2))
