# Owner Training Guide — Laredo Dental AI Receptionist

## What It Does

Your AI receptionist answers patient questions on WhatsApp 24/7:
- Office hours, location, parking
- Insurance accepted (Delta Dental, Aetna, Cigna, MetLife, Guardian, BCBS)
- Services offered (cleanings, fillings, crowns, braces, whitening, implants)
- New patient intake (collects name, phone, preferred time)
- Remembers returning patients by name and last visit date

## How It Works

1. Patient texts your WhatsApp Business number
2. AI answers immediately (under 5 seconds)
3. If AI doesn't know → you get an SMS alert
4. You reply to the SMS → AI relays to patient within 30 seconds

## Escalation: When You Get an SMS

You'll receive an SMS like:
```
Patient: María García
Question: ¿Necesito una endodoncia?
Phone: 521234567890@c.us
I don't know the answer. Reply to this message to respond.
```

**Reply directly to the SMS** and the AI will relay your response to the patient.

### Escalation triggers:
- **Medical advice** — treatment questions, diagnoses, symptoms
- **Pricing** — cost questions about procedures
- **Appointment booking** — specific date/time booking requests
- **Unknown** — anything the AI can't answer

**Never** confirm appointments or give medical advice through the AI — always escalate.

## Daily Checklist

- [ ] Morning: Verify gateway is healthy — `curl http://localhost:8000/health`
- [ ] Review escalated conversations from overnight (check escalation logs)
- [ ] Respond to any pending SMS escalations
- [ ] Check for new patient intakes that need follow-up calls
- [ ] Update FAQ answers if common new questions emerge

## Adding / Updating Office Info

Edit `faq/knowledge.py` to update:
- Office hours
- Address and parking info
- Insurance carriers accepted
- Services list

Changes take effect on next gateway restart.

## Understanding Patient Memory

The system remembers:
- Patient's name and phone number
- Last appointment date
- Number of conversations they've had
- If they message from a new number, it will ask for identity verification

## Pilot Success Metrics

| Metric | Target | How to Check |
|--------|--------|-------------|
| Conversations handled | 30+ per week | `/health` endpoint shows total_conversations |
| Accuracy | 95%+ (no made-up info) | Review escalated conversations weekly |
| Response time | Under 5 seconds | Monitor gateway response times |
| Escalation rate | Under 20% of conversations | Track escalated vs total messages |
| Patient satisfaction | No complaints about wrong info | Weekly review of all escalations |

## Support

For technical issues: check `DEPLOY.md` for troubleshooting.
For gateway issues: contact the development team.
Emergency: call the office phone directly — the AI is a helper, not a replacement.
