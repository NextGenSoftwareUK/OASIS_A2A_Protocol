# Troubleshooting: A2A API Endpoints Returning 404

## Problem

All A2A endpoints are returning 404 errors:
- `/api/a2a/karma` → 404
- `/api/a2a/nft/reputation` → 404
- `/api/a2a/nft/service-certificate` → 404
- `/api/a2a/karma/award` → 404

## Root Cause

The new A2A endpoints we added are **not in the running API server**. The `A2AController.cs` file with the new endpoints exists but:

1. **File is untracked** - Not committed to git yet
2. **API needs to be rebuilt** - The running server was started before new endpoints were added
3. **API needs to be restarted** - After rebuilding

## Solution

### Option 1: Rebuild and Restart API (Recommended)

1. **Stop the current API server** (Ctrl+C in the terminal running it)

2. **Rebuild the project:**
   ```bash
   cd ONODE/NextGenSoftware.OASIS.API.ONODE.WebAPI
   dotnet build
   ```

3. **Restart the API:**
   ```bash
   dotnet run --urls http://localhost:5003
   ```

4. **Verify endpoints are available:**
   ```bash
   curl http://localhost:5003/swagger/index.html
   # Look for A2A endpoints in Swagger UI
   ```

### Option 2: Check Route Case Sensitivity

ASP.NET Core routes might be case-sensitive. Try:
- `/api/A2A/karma` (uppercase) instead of `/api/a2a/karma` (lowercase)
- The test script now tries both automatically

### Option 3: Verify Controller is Loaded

Check if A2AController is being discovered:

1. Check Swagger UI: `http://localhost:5003/swagger`
2. Look for "A2A" controller section
3. Verify all endpoints are listed

## Quick Fix Script

Run this to check if endpoints exist:

```bash
# Check uppercase route
curl -X GET http://localhost:5003/api/A2A/karma \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check lowercase route  
curl -X GET http://localhost:5003/api/a2a/karma \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check Swagger
curl http://localhost:5003/swagger/v1/swagger.json | grep -i "a2a"
```

## Expected Behavior After Fix

After rebuilding and restarting:
- ✅ Endpoints should return 401 (Unauthorized) instead of 404
- ✅ With valid token, endpoints should work
- ✅ Swagger UI should show all A2A endpoints

## Next Steps

1. Rebuild and restart the API
2. Run the test script again
3. Endpoints should work properly

---

**Note:** The A2AController.cs file exists but needs to be compiled and the server restarted for the endpoints to be available.

