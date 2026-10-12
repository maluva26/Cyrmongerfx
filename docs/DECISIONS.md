# Decisions Log

## 1. Backend API uses SQLite for local dev
Supabase connection requires a pooled Postgres connection string. Local dev uses SQLite for speed and simplicity. CI uses SQLite too.

## 2. No torch/opencv in backend requirements
Free-tier mode requires the API process to stay under ~400 MB RAM. Inference goes through `INFERENCE_SERVICE_URL`.

## 3. LLM provider is Gemini by default
Anthropic API is not free. Gemini free tier is the default. AnthropicProvider is available for later upgrade.

## 4. Mock detector is the only simulated output
Simulated detections are allowed only when `INFERENCE_BACKEND=mock` and `ALLOW_DEMO_MODEL=True`. Production refuses to start with mock unless explicitly allowed.

## 5. Access token in memory only
The frontend keeps the JWT access token in a React context (memory). Refresh uses the httpOnly cookie.

## 6. Client-side image compression
Reduces bandwidth for low-end Android phones on expensive data. Max long edge 1280px, WebP quality 0.8.

## 7. RLS on all tables with deny-all default
Django accesses data via the service role. RLS blocks direct PostgREST access.
