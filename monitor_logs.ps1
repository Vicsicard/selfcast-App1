Write-Host "Starting log monitor - will check every 15 minutes"
Write-Host "Press Ctrl+C to stop monitoring"

while ($true) {
    Clear-Host
    Write-Host "=== Log Monitor ===" -ForegroundColor Cyan
    & .\venv\Scripts\python.exe check_logs.py
    Write-Host "`nNext check in 15 minutes..." -ForegroundColor Gray
    Start-Sleep -Seconds 900  # 15 minutes
}
