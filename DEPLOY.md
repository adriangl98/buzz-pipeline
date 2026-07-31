# Laredo Dental AI Receptionist — Deployment Guide

## Overview

AI receptionist on WhatsApp that remembers patients, answers FAQs, and escalates to owner.
Built with OpenWA + Hermes Gateway + DeepSeek.

## Prerequisites

- VPS running Docker (Hetzner CX22, $5/mo)
- WhatsApp Business number
- Domain or Tailscale for webhook exposure

## Quick Start

```bash
git clone https://github.com/adriangl98/buzz-pipeline.git
cd buzz-pipeline

# Start the stack
docker compose up -d

# Check health
curl http://localhost:8000/health
# → {"status": "healthy", "patients": 0}
```

## Architecture

```
WhatsApp → OpenWA (Docker) → Hermes Gateway (FastAPI) → Patient
                                    │
                              FAQ + Memory + Escalation
```

## Services

| Service | Port | Purpose |
|---------|------|---------|
| openwa | 3000 | WhatsApp Web bridge |
| gateway | 8000 | Hermes Gateway (FastAPI) |

## Configuration

### Environment Variables (.env)

```env
OPENWA_URL=http://openwa:3000
OWNER_PHONE=+15551234567
```

### Connecting WhatsApp

1. Open OpenWA dashboard at `http://<vps>:3000`
2. Scan QR code with WhatsApp Business
3. Verify connection sends test message

### Webhook Setup

Configure OpenWA to forward messages to the gateway:

```
Webhook URL: http://gateway:8000/webhook
Events: message
```

## Verification Checklist

- [ ] `GET /health` returns healthy
- [ ] Send WhatsApp message → receives echo
- [ ] FAQ questions answered correctly
- [ ] Returning patients greeted by name
- [ ] Medical questions trigger escalation

## Owner Training

### What the agent handles
- Office hours, location, parking
- Insurance accepted
- Services offered
- New patient intake
- Patient memory (name, last visit)

### What triggers escalation
- Medical advice questions (treatment, diagnosis)
- Pricing/cost questions
- Appointment booking
- Unknown questions

### How escalation works
1. Agent detects trigger → sends SMS to owner
2. Owner replies → agent relays to patient
3. Response tracked in logs

## Pilot Metrics (Week 1)

| Metric | Target |
|--------|--------|
| Conversations | 30+ |
| Accuracy | >95% |
| Response time | <5 seconds |
| Wrong answers | 0 |

## Troubleshooting

| Issue | Check |
|-------|-------|
| Gateway 502 | OpenWA reachable? `curl http://openwa:3000` |
| No WhatsApp messages | QR code still active? Re-scan |
| Slow responses | Check VPS CPU/RAM, Docker logs |
| Escalation not firing | Owner phone set in .env? |
