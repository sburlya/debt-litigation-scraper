# Debt AI Litigation Scraper

Microservice for scraping court cases from instante.justice.md

## Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run server
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Health Check
```
GET /health
```

### Scrape Litigation
```
POST /api/litigation
Content-Type: application/json

{
  "company_name": "Energocom"
}
```

Response:
```json
{
  "success": true,
  "company_name": "Energocom",
  "total_cases": 34,
  "cases": [
    {
      "case_number": "2-23118768-02-2a-28062024",
      "court": "Curtea de Apel Centru",
      "parties": "MERLAN SERGIU vs. SOCIETATEA PE ACȚIUNI ENERGOCOM",
      "filing_date": "2025-05-28",
      "hearing_date": "2025-11-22",
      "status": null
    }
  ],
  "scraped_at": "2025-02-01T12:00:00",
  "error": null
}
```

## Deployment (Railway)

1. Create new project on railway.app
2. Connect GitHub repository
3. Set environment variables:
   - `ALLOWED_ORIGINS=https://debt.md,http://localhost:5173`
4. Deploy

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ALLOWED_ORIGINS` | `http://localhost:5173,https://debt.md` | Comma-separated CORS origins |
