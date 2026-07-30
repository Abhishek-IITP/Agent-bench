# Database Setup Guide

This guide covers setting up the PostgreSQL database for AgentBench, including prerequisites, step-by-step installation, environment configuration, and troubleshooting.

## Overview

AgentBench uses PostgreSQL 16 running in a Docker container to store:
- Task metadata and configurations
- Agent configurations
- Benchmark run records
- Test results and evaluation metrics
- Replay traces for debugging
- Aggregated analytics and health classifications

The database is configured via Docker Compose for easy setup and management.

## Prerequisites

### Required Software

1. **Docker Desktop** (Windows/macOS) or **Docker Engine** (Linux)
   - Version: 20.10 or higher
   - Download: https://www.docker.com/products/docker-desktop/
   - Verify installation: `docker --version`

2. **Docker Compose**
   - Included with Docker Desktop
   - For Linux: https://docs.docker.com/compose/install/
   - Verify installation: `docker compose version`

3. **Python 3.11 or higher**
   - Required for the Python runner
   - Verify installation: `python --version`

4. **Bun 1.0 or higher** (for API backend)
   - Installation: https://bun.sh/docs/installation
   - Verify installation: `bun --version`

### System Requirements

- **RAM**: Minimum 4GB available (8GB recommended)
- **Disk Space**: 2GB for Docker images and database storage
- **Ports**: Port 5432 must be available (PostgreSQL default)

### Checking Port Availability (Windows)

```cmd
netstat -ano | findstr :5432
```

If the port is in use, you'll need to either:
- Stop the service using that port
- Configure PostgreSQL to use a different port in `docker-compose.yml`

## Step-by-Step Setup

### 1. Clone and Navigate to Repository

```cmd
cd e:\Abhishek-IITP\ABHILIB\agent-bench
```

### 2. Configure Environment Variables

Copy the example environment file and configure it:

```cmd
copy .env.example .env
```

Edit `.env` file with your settings:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=agentbench
DB_USER=postgres
DB_PASSWORD=postgres

# API Configuration
PORT=3001
API_URL=http://localhost:3001

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:3001
```

**Security Note**: For production environments, use strong passwords and never commit `.env` to version control.

### 3. Review Docker Compose Configuration

The `docker-compose.yml` file defines the database service:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: agentbench-db
    environment:
      POSTGRES_DB: agentbench
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./runner/db/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**Key Features**:
- **Auto-initialization**: Schema is applied automatically on first startup
- **Persistent storage**: Data survives container restarts via named volume
- **Health checks**: Ensures database is ready before accepting connections

### 4. Start the Database

Start the PostgreSQL container:

```cmd
docker compose up -d postgres
```

**Expected Output**:
```
[+] Running 2/2
 ✔ Network agent-bench_default  Created
 ✔ Container agentbench-db      Started
```

### 5. Verify Container is Running

Check container status:

```cmd
docker ps | findstr agentbench-db
```

**Expected Output**:
```
abc123def456   postgres:16-alpine   "docker-entrypoint.s..."   10 seconds ago   Up 8 seconds (healthy)   0.0.0.0:5432->5432/tcp   agentbench-db
```

Look for **(healthy)** status - this indicates the database is ready.

### 6. Verify Schema Initialization

Check that all tables were created:

```cmd
docker exec -it agentbench-db psql -U postgres -d agentbench -c "\dt"
```

**Expected Output**:
```
                          List of relations
 Schema |             Name              | Type  |  Owner
--------+-------------------------------+-------+----------
 public | agents                        | table | postgres
 public | execution_metrics             | table | postgres
 public | multi_run_metrics             | table | postgres
 public | replays                       | table | postgres
 public | results                       | table | postgres
 public | runs                          | table | postgres
 public | task_difficulty_calibration   | table | postgres
 public | task_health                   | table | postgres
 public | tasks                         | table | postgres
(9 rows)
```

You should see 9 tables listed.

### 7. Test Database Connection (Python)

Run the connection test script:

```cmd
python scripts\test-connection.py
```

**Expected Output**:
```
✓ Connected to PostgreSQL database
✓ Database: agentbench
✓ PostgreSQL version: 16.x
✓ All 9 tables found:
  - tasks
  - agents
  - runs
  - results
  - replays
  - execution_metrics
  - multi_run_metrics
  - task_health
  - task_difficulty_calibration
✓ Database connection test PASSED
```

### 8. Install Python Dependencies

Install the AgentBench package with database support:

```cmd
pip install -e .
```

This installs the `psycopg2` database driver required for PostgreSQL connections.

### 9. Verify API Backend Connection (Optional)

If you're using the API backend, start it and verify the connection:

```cmd
cd dashboard\api
bun install
bun run src/index.ts
```

Then test the health endpoint:

```cmd
curl http://localhost:3001/api/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Environment Variables Reference

### Database Connection

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DB_HOST` | Database hostname | `localhost` | Yes |
| `DB_PORT` | Database port | `5432` | Yes |
| `DB_NAME` | Database name | `agentbench` | Yes |
| `DB_USER` | Database username | `postgres` | Yes |
| `DB_PASSWORD` | Database password | `postgres` | Yes |

### API Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | API server port | `3001` | No |
| `API_URL` | API base URL | `http://localhost:3001` | No |

### Frontend Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEXT_PUBLIC_API_URL` | API URL for browser | `http://localhost:3001` | Yes |

## Verification Checklist

Use this checklist to verify your setup:

- [ ] Docker Desktop is running
- [ ] Port 5432 is available
- [ ] `.env` file exists and is configured
- [ ] `docker compose up -d postgres` completes successfully
- [ ] Container shows **(healthy)** status in `docker ps`
- [ ] All 9 tables exist in database
- [ ] `python scripts\test-connection.py` passes
- [ ] Python dependencies installed with `pip install -e .`
- [ ] (Optional) API health check returns `{"status": "healthy"}`

## Troubleshooting

### Issue: Port 5432 Already in Use

**Symptoms**:
```
Error response from daemon: Ports are not available: exposing port TCP 0.0.0.0:5432 -> 0.0.0.0:0: listen tcp 0.0.0.0:5432: bind: Only one usage of each socket address
```

**Solution 1**: Stop the conflicting service

1. Find what's using port 5432:
```cmd
netstat -ano | findstr :5432
```

2. Stop the service or kill the process using that port

**Solution 2**: Change the PostgreSQL port

Edit `docker-compose.yml`:
```yaml
ports:
  - "5433:5432"  # Use port 5433 instead
```

Update `.env`:
```bash
DB_PORT=5433
```

Then restart: `docker compose up -d postgres`

---

### Issue: Container Starts but Shows "unhealthy"

**Symptoms**:
```
agentbench-db   postgres:16-alpine   Up 30 seconds (unhealthy)
```

**Solution**:

1. Check container logs:
```cmd
docker logs agentbench-db
```

2. Look for errors in the output

3. Common causes:
   - Corrupted data volume (solution: recreate volume)
   - Permission issues (solution: check Docker permissions)
   - Insufficient memory (solution: increase Docker memory limit)

4. Recreate container and volume:
```cmd
docker compose down -v
docker compose up -d postgres
```

---

### Issue: Schema Not Applied (No Tables)

**Symptoms**:
```
ERROR:  relation "tasks" does not exist
```

**Solution**:

1. Verify schema file exists:
```cmd
dir runner\db\schema.sql
```

2. Manually apply schema:
```cmd
docker exec -i agentbench-db psql -U postgres -d agentbench < runner\db\schema.sql
```

3. Verify tables were created:
```cmd
docker exec -it agentbench-db psql -U postgres -d agentbench -c "\dt"
```

---

### Issue: Connection Refused

**Symptoms**:
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**Solution**:

1. Verify container is running:
```cmd
docker ps | findstr agentbench-db
```

2. Check container health:
```cmd
docker exec agentbench-db pg_isready -U postgres
```

3. Restart container if needed:
```cmd
docker compose restart postgres
```

4. Check firewall settings (Windows Defender may block Docker)

---

### Issue: Python Connection Test Fails

**Symptoms**:
```
ModuleNotFoundError: No module named 'psycopg2'
```

**Solution**:

1. Install psycopg2:
```cmd
pip install psycopg2-binary
```

2. Or reinstall AgentBench with dependencies:
```cmd
pip install -e .
```

---

### Issue: Permission Denied on Volume

**Symptoms**:
```
ERROR: for postgres  Cannot start service postgres: error while mounting volume
```

**Solution**:

1. Ensure Docker has permission to access the directory
2. On Windows: Add the directory to Docker Desktop's File Sharing settings
3. Restart Docker Desktop
4. Try again: `docker compose up -d postgres`

---

### Issue: Container Exits Immediately

**Symptoms**:
```
docker ps  # Shows no agentbench-db container
docker ps -a  # Shows Exited status
```

**Solution**:

1. Check logs for the error:
```cmd
docker logs agentbench-db
```

2. Common causes:
   - Invalid environment variables in `docker-compose.yml`
   - Corrupted PostgreSQL data directory
   - Incompatible Docker version

3. Remove container and volume, then recreate:
```cmd
docker compose down -v
docker compose up -d postgres
```

## Next Steps

Once the database is set up and verified:

1. **Run benchmarks**: See [DATABASE-OPERATIONS.md](DATABASE-OPERATIONS.md) for running benchmarks with database storage
2. **Query data**: Use the API endpoints to retrieve benchmark results
3. **View dashboard**: Start the Next.js dashboard to visualize results
4. **Backup data**: See [DATABASE-OPERATIONS.md](DATABASE-OPERATIONS.md) for backup procedures

## Additional Resources

- [DATABASE-OPERATIONS.md](DATABASE-OPERATIONS.md) - Database operations and maintenance
- [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md) - Migrating from file-based storage
- [PostgreSQL Documentation](https://www.postgresql.org/docs/16/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

## Getting Help

If you encounter issues not covered in this guide:

1. Check the container logs: `docker logs agentbench-db`
2. Verify your Docker installation: `docker info`
3. Check GitHub Issues for similar problems
4. Open a new issue with:
   - Operating system and version
   - Docker version (`docker --version`)
   - Error messages and logs
   - Steps to reproduce the issue
