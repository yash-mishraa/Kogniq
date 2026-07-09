# Health Verification Guide

This guide details how to verify the health of Kogniq's containerized local development infrastructure.

## 1. Verify Containers
Run the status script from the repository root:
- **Windows:** `.\scripts\status.bat`
- **Linux/macOS:** `./scripts/status.sh`

**Expected Output:**
You should see three containers running with a health status of `(healthy)`:
- `kogniq_postgres`
- `kogniq_redis`
- `kogniq_pgadmin`

## 2. Verify Ports & Network
Ensure the following ports are successfully bound on `localhost`:
- **PostgreSQL:** `5432` (or custom `POSTGRES_PORT` from `.env`)
- **Redis:** `6379` (or custom `REDIS_PORT` from `.env`)
- **pgAdmin:** `5050` (or custom `PGADMIN_PORT` from `.env`)

## 3. Verify pgAdmin Reachability
1. Open your web browser.
2. Navigate to [http://localhost:5050](http://localhost:5050).
3. Ensure the login screen appears.
4. Login using the credentials defined in your `.env` file (`PGADMIN_EMAIL` and `PGADMIN_PASSWORD`).

## 4. Verify PostgreSQL Data Persistence
1. Login to pgAdmin.
2. Create a test database.
3. Restart the containers using the reset/restart scripts.
4. Verify the test database still exists (validating `postgres_data` volume persistence).

## 5. Verify Redis Health
1. Access the Redis container: `docker exec -it kogniq_redis redis-cli`
2. Run `PING`.
3. **Expected Output:** `PONG`
