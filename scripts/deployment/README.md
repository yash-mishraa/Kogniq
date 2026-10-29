# Deployment Operations & Verification

Operational utilities and verification procedures for staging and production deployments.

---

## Deployment Verification Workflow

1. **Verify Backend Health**:
   ```bash
   curl -fsS https://kogniq-api.onrender.com/api/v1/system/health
   # Returns: {"status":"healthy"}
   ```

2. **Verify System Telemetry & Index State**:
   ```bash
   curl -fsS https://kogniq-api.onrender.com/api/v1/system/overview
   ```

3. **Verify Frontend Route Proxying**:
   ```bash
   curl -fsS https://kogniq.vercel.app/api/v1/auth/csrf
   ```

---

## Production Pre-Flight Checklist
- [x] Environment variable `KOGNIQ_API_ENVIRONMENT=production` set on container host.
- [x] Model identifier set to `gemini-3.5-flash-lite` with valid `GEMINI_API_KEY`.
- [x] Persistent database directory `/app/data` configured.
- [x] Frontend `BACKEND_URL` environment variable properly configured in Vercel project settings.
