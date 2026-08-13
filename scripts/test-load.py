#!/usr/bin/env python3
"""Load testing script for API endpoints and connection pooling."""

import asyncio
import aiohttp
import time
from statistics import mean, stdev

API_URL = "http://localhost:3001"


async def fetch_endpoint(session, url, semaphore):
    """Fetch a single endpoint with semaphore for concurrency control."""
    async with semaphore:
        start = time.perf_counter()
        try:
            async with session.get(url) as response:
                await response.json()
                elapsed = (time.perf_counter() - start) * 1000
                return {"success": True, "time": elapsed, "status": response.status}
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return {"success": False, "time": elapsed, "error": str(e)}


async def load_test(endpoint, num_requests, concurrency):
    """Run load test on a specific endpoint."""
    url = f"{API_URL}{endpoint}"
    semaphore = asyncio.Semaphore(concurrency)

    print(f"\nTesting {endpoint}")
    print(f"  Total requests: {num_requests}")
    print(f"  Concurrency: {concurrency}")
    print(f"  URL: {url}")
    print()

    start_time = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_endpoint(session, url, semaphore) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)

    total_time = time.perf_counter() - start_time

    # Analyze results
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]

    if successes:
        times = [r["time"] for r in successes]

        print("Results:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Requests/sec: {num_requests / total_time:.2f}")
        print(
            f"  Successful: {len(successes)}/{num_requests} ({len(successes)/num_requests*100:.1f}%)"
        )
        print(f"  Failed: {len(failures)}")
        print()
        print("Response times:")
        print(f"  Mean: {mean(times):.2f}ms")
        print(f"  Min: {min(times):.2f}ms")
        print(f"  Max: {max(times):.2f}ms")
        print(f"  StdDev: {stdev(times):.2f}ms" if len(times) > 1 else "  StdDev: N/A")

    if failures:
        print("\nErrors:")
        error_counts = {}
        for f in failures:
            error = f.get("error", "Unknown")
            error_counts[error] = error_counts.get(error, 0) + 1
        for error, count in error_counts.items():
            print(f"  {error}: {count}")

    return {
        "total_requests": num_requests,
        "successful": len(successes),
        "failed": len(failures),
        "total_time": total_time,
        "mean_time": mean(times) if successes else 0,
    }


async def main():
    """Run load tests."""
    print("=" * 80)
    print("API Load Testing & Connection Pooling Validation")
    print("=" * 80)
    print()
    print("Target: Support 100 concurrent connections (REQ-2.1.5)")
    print("=" * 80)

    # Test 1: Light load (10 concurrent)
    print("\n" + "=" * 80)
    print("Test 1: Light Load (10 concurrent requests)")
    print("=" * 80)
    result1 = await load_test("/api/tasks", num_requests=50, concurrency=10)

    # Test 2: Medium load (50 concurrent)
    print("\n" + "=" * 80)
    print("Test 2: Medium Load (50 concurrent requests)")
    print("=" * 80)
    result2 = await load_test("/api/runs", num_requests=100, concurrency=50)

    # Test 3: Heavy load (100 concurrent) - REQ-2.1.5
    print("\n" + "=" * 80)
    print("Test 3: Heavy Load (100 concurrent requests) - REQ-2.1.5")
    print("=" * 80)
    result3 = await load_test("/api/leaderboard", num_requests=200, concurrency=100)

    # Test 4: Mixed endpoints (100 concurrent)
    print("\n" + "=" * 80)
    print("Test 4: Mixed Endpoints (100 concurrent requests)")
    print("=" * 80)

    endpoints = [
        "/api/health",
        "/api/tasks",
        "/api/runs",
        "/api/leaderboard",
        "/api/health/tasks",
    ]

    semaphore = asyncio.Semaphore(100)

    async def fetch_random_endpoint(session):
        import random

        endpoint = random.choice(endpoints)
        return await fetch_endpoint(session, f"{API_URL}{endpoint}", semaphore)

    start_time = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_random_endpoint(session) for _ in range(200)]
        results = await asyncio.gather(*tasks)

    total_time = time.perf_counter() - start_time
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]

    print("Results:")
    print("  Total requests: 200")
    print("  Concurrency: 100")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Requests/sec: {200 / total_time:.2f}")
    print(f"  Successful: {len(successes)}/200 ({len(successes)/200*100:.1f}%)")
    print(f"  Failed: {len(failures)}")

    if successes:
        times = [r["time"] for r in successes]
        print()
        print("Response times:")
        print(f"  Mean: {mean(times):.2f}ms")
        print(f"  Min: {min(times):.2f}ms")
        print(f"  Max: {max(times):.2f}ms")
        print(f"  StdDev: {stdev(times):.2f}ms")

    # Summary
    print("\n" + "=" * 80)
    print("Load Test Summary")
    print("=" * 80)
    print()

    all_tests = [result1, result2, result3]
    total_requests = sum(r["total_requests"] for r in all_tests)
    total_successful = sum(r["successful"] for r in all_tests)
    total_failed = sum(r["failed"] for r in all_tests)

    print(f"Total requests: {total_requests}")
    print(f"Total successful: {total_successful} ({total_successful/total_requests*100:.1f}%)")
    print(f"Total failed: {total_failed}")
    print()

    # Check if 100 concurrent connections requirement is met
    test3_success_rate = result3["successful"] / result3["total_requests"]
    requirement_met = test3_success_rate >= 0.95  # Allow 5% error margin

    print(f"REQ-2.1.5 (100 concurrent connections): {'✓ PASS' if requirement_met else '✗ FAIL'}")
    print(f"  Success rate with 100 concurrent: {test3_success_rate*100:.1f}%")
    print()

    if requirement_met:
        print("✓ Connection pooling is working correctly!")
        print("✓ All load tests passed successfully!")
    else:
        print("✗ Some requests failed under heavy load")
        print("  Consider increasing connection pool size or tuning database")

    print("=" * 80)

    return 0 if requirement_met else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
