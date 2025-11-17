# Transferencias Service

Microservice for managing transfers using FastAPI and Firestore.

Project: TRANSFERENCIASCHUNO
ID: transferenciaschuno
Number: 679919655068
Organization: ucb.edu.bo

## Setup
- Ensure secrets/auth/transferencias-service-credentials.json is present.
- Run with Docker: `docker-compose up`

## Endpoints
- Base: /api/transferencias
- GET / (query: cuenta_id, tipo)
- GET /{id}
- POST / (body as described)