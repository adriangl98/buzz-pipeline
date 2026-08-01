# Hermes Local MVP — Deployment Guide

## Prerequisites

- **VPS:** Hetzner CX22 (2 vCPU, 4 GB RAM) or equivalent
- **OS:** Ubuntu 22.04 LTS
- **WhatsApp Business:** A phone number registered with WhatsApp Business
- **Docker:** 24+ and docker-compose

## Quick Start

```bash
git clone https://github.com/adriangl98/buzz-pipeline.git
cd buzz-pipeline
git checkout feature/builder-5
docker compose up -d
```

Then visit `http://<vps-ip>:3000` and scan the QR code with WhatsApp Business.

## Architecture

```
Patient (WhatsApp) → OpenWA (:3000) → Hermes Gateway (:8000)
                                          ├── FAQ (keyword matching)
                                          ├── Patient Memory (Honcho)
                                          └── Escalation (SMS)
```

## Verification

```bash
# Health check
curl http://localhost:8000/health
# → {"status":"healthy","topics":5}

# Pilot test suite
source venv/bin/activate
pytest tests/test_pilot.py -v
```

## FAQ Reference

| Topic | EN Keywords | ES Keywords |
|-------|------------|-------------|
| hours | hour, open, close | horario, hora, abierto |
| location | where, located, address | donde, ubicado, direccion |
| insurance | insurance, delta, aetna | seguro, aseguradora |
| services | cleaning, braces, crown | limpieza, frenos, corona |
| new_patient | new patient, first time | nuevo paciente, primera vez |

## Monitoring

```bash
docker logs hermes-gateway -f
docker logs openwa -f
htop
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| OpenWA not connecting | `docker compose restart openwa` |
| Gateway 502 errors | Check OpenWA reachable: `curl http://openwa:3000` |
| FAQ not matching | Verify keywords in `faq/knowledge.py` |
| Slow responses | Check CPU/memory: `htop` |
