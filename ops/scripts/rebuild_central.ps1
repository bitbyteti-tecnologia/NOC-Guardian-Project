Write-Host "=== NOC GUARDIAN: Forcing Central Rebuild ==="
Write-Host "Reason: Applying code changes to Docker Container"

# Force rebuild of central service only
docker compose up -d --build central

# Check status
docker compose ps central

Write-Host "=== Rebuild Complete. Verify Swagger at /docs ==="
