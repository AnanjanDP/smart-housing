#!/usr/bin/env bash

echo "=== StayMatch Service Health Check ==="

check_service() {
    local name=$1
    local url=$2
    local code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    if [ "$code" -eq 200 ] || [ "$code" -eq 302 ]; then
        echo "[OK] $name ($url) - Status $code"
    else
        echo "[FAIL] $name ($url) - Status $code"
    fi
}

check_service "Django Core API" "http://localhost:8000/api/v1/health/"
check_service "Search Microservice" "http://localhost:8001/health"
check_service "Recommendation Microservice" "http://localhost:8002/health"
check_service "Prometheus" "http://localhost:9090/-/healthy"
