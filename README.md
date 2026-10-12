# Cyrmonger Algo Fx

Forex education, chart analysis, and learning tools for retail traders. **Not financial advice. No broker execution.**

## Stack

- Backend: Django 5 + DRF + SimpleJWT
- Frontend: Next.js 14 (App Router) + TypeScript + Tailwind CSS
- Database: Supabase PostgreSQL (session pooler)
- Storage: Supabase private bucket `chart-uploads`
- AI: Mock detector (dev) / Hugging Face Space (production)
- LLM: Google Gemini (free tier default) / Anthropic Claude (optional)
- Market data: Twelve Data (cached)

## Local Setup

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py createsuperuser`
5. `python manage.py runserver`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`
4. Open http://localhost:3000

## Deploy Free Tier

1. Supabase: create project, private bucket `chart-uploads`, run `supabase/schema.sql` and `supabase/rls.sql`
2. Hugging Face Space: deploy `inference-service/` as a FastAPI Space
3. Render: deploy backend (free web service, sleeps when idle)
4. Vercel: deploy frontend
5. UptimeRobot: ping `/api/v1/health` every 5 min
6. GitHub Actions: set secrets for purge workflow

## Notes
- Free-tier mode (`FREE_TIER_MODE=True`) applies conservative defaults.
- Mock model is labelled `DEMO MODEL` in the UI.
- Confidence scores are model scores, not probabilities of profit.
- All detections, signals and calculations carry an educational disclaimer.
