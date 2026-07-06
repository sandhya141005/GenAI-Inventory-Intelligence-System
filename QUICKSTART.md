# Quick Start Guide

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 14+
- OpenAI API Key

## Setup Steps

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set:
# - DATABASE_URL=postgresql://user:password@localhost/inventory_db
# - OPENAI_API_KEY=your_openai_key

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

Backend runs on: http://localhost:8000

### 2. Frontend Setup

```bash
# From project root
npm install

# Optional: Create .env.local if backend is not on localhost:8000
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start frontend
npm run dev
```

Frontend runs on: http://localhost:3000

### 3. Create First User

1. Navigate to http://localhost:3000
2. Click "Sign up"
3. Fill in:
   - Full Name: Your Name
   - Email: you@example.com
   - Password: (minimum 8 characters)
4. Click "Create Account"
5. You'll be automatically logged in and redirected to `/overview`

## Testing the Integration

### Test Analytics (Rule-Based)
1. Visit `/overview` - See KPIs and recommendations
2. Visit `/inventory` - See inventory table
3. Visit `/analytics` - See charts

### Test AI Features (OpenAI-Powered)
1. Visit `/` (home) - AI Copilot chat interface
2. Type: "What products are at risk of stocking out?"
3. Visit `/ai-reports/morning-brief` - See AI-generated brief
4. Visit `/ai-reports/weekly-report` - See AI-generated report
5. Visit `/ai-reports/executive-summary` - See AI summary

### Test Authentication
1. Click "Sign Out" in sidebar
2. Try to visit `/overview` → Should redirect to `/login`
3. Log back in → Should redirect to `/overview`

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running
- Check DATABASE_URL in .env
- Run `alembic upgrade head` to apply migrations

### Frontend shows "Unauthorized"
- Check backend is running on port 8000
- Clear browser localStorage and log in again
- Check NEXT_PUBLIC_API_URL matches backend URL

### AI features not working
- Check OPENAI_API_KEY is set in backend/.env
- Check backend logs for errors
- Ensure you're logged in (AI endpoints require auth)

### "No data available" in reports
- This is normal for empty database
- Analytics will show zeros/empty states
- AI will report "no data to analyze"

## Next Steps

- Add demo data (optional): Create sample products, stores, sales records
- Explore AI prompts: Try different questions in the copilot
- Review code: Check INTEGRATION_COMPLETE.md for implementation details
