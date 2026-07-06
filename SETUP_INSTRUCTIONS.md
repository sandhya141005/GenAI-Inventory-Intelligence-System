# Demo Setup Instructions

## Quick Setup (2 Steps)

### Step 1: Generate Demo Data

```bash
cd backend
python scripts/generate_demo_data_simple.py
```

**Expected Output:**
```
✅ Created 10 stores
✅ Created 56 products
✅ Generated warehouse inventory
✅ Generated 9105 sales transactions
✅ Generated 7 transfers
```

### Step 2: Create Demo User

You have **3 options**:

#### Option A: Use Complete Setup Script (Easiest)

**Backend must be running first:**
```bash
# Terminal 1 - Start backend
cd backend
uvicorn app.main:app --reload
```

Then run the setup script:
```bash
# Terminal 2 - In backend directory
.\scripts\complete_demo_setup.ps1  # Windows
# OR
bash scripts/complete_demo_setup.sh  # Linux/Mac (if created)
```

#### Option B: Via Frontend Signup (Simplest)

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Visit http://localhost:3000/signup
4. Create account:
   - Email: `demo@mckinsey.com`
   - Password: `demo1234`
   - Name: `McKinsey Demo User`

#### Option C: Via API (curl/Postman)

**Backend must be running:**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@mckinsey.com",
    "password": "demo1234",
    "full_name": "McKinsey Demo User"
  }'
```

## Verify Setup

1. **Check Database has data:**
```bash
cd backend
python -c "
from app.db.session import SessionLocal
from app.models.analytics_data import Product, Sale
db = SessionLocal()
print(f'Products: {db.query(Product).count()}')
print(f'Sales: {db.query(Sale).count()}')
"
```

Expected: Products: 56, Sales: ~9000

2. **Login to Frontend:**
   - URL: http://localhost:3000
   - Email: demo@mckinsey.com
   - Password: demo1234

3. **Test Analytics:**
   - Visit `/overview` - Should show KPIs and recommendations
   - Visit `/inventory` - Should show 56 products
   - Visit `/analytics` - Should show charts with data

4. **Test AI Copilot:**
   - Visit `/` (home)
   - Click any suggested prompt
   - AI should respond with analysis

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'jose'" or "passlib"

**Solution:** This is expected. Use the simplified scripts:
- `generate_demo_data_simple.py` (no dependencies)
- Create user via frontend signup or API

### Issue: "No data in analytics"

**Solution:** Run data generation script:
```bash
cd backend
python scripts/generate_demo_data_simple.py
```

### Issue: "Cannot login - user not found"

**Solution:** Create user via:
- Frontend signup at http://localhost:3000/signup, OR
- API endpoint (see Option C above)

### Issue: "AI Copilot shows errors"

**Possible causes:**
1. Backend not running → Start with `uvicorn app.main:app --reload`
2. No data in database → Run `generate_demo_data_simple.py`
3. OpenAI API key not set → Check `backend/.env` has `OPENAI_API_KEY`
4. Not logged in → Login at http://localhost:3000/login

## File Reference

### Data Generation
- `backend/scripts/generate_demo_data_simple.py` - Main data generator (no auth deps)
- `backend/scripts/complete_demo_setup.ps1` - Complete setup script (Windows)
- `backend/scripts/test_models.py` - Verify model imports

### Documentation
- `DEMO_GUIDE.md` - Complete demo walkthrough for presentations
- `DEMO_DATA_SUMMARY.md` - Technical details on generated data
- `README_DEMO.md` - Demo setup and usage guide

## What Was Generated

✅ **56 Automotive Products:**
- Engine oils, filters, brake pads, tyres
- Batteries, suspension, cooling systems
- Realistic Indian market pricing

✅ **10 Locations:**
- 1 warehouse (Delhi Central Hub)
- 9 retail stores across India

✅ **~9,000 Sales Transactions:**
- 90 days of history
- Realistic demand patterns
- Seasonal variations

✅ **7 Transfers:**
- Stockout prevention
- Overstock rebalancing
- In-transit shipments

✅ **Expected Analytics:**
- Revenue at risk: INR 50K-150K
- 10-12 products at stockout risk
- 5-7 products overstocked
- Multiple transfer opportunities

## Ready to Demo!

Once setup is complete:

1. **Backend:** http://localhost:8000
2. **Frontend:** http://localhost:3000
3. **Login:** demo@mckinsey.com / demo1234

Try these AI queries:
- "Which automotive parts are at risk of stocking out in the next 7 days?"
- "Generate an executive summary of current inventory health"
- "Recommend inventory transfers to balance stock levels"
