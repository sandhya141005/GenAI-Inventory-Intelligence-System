#!/bin/bash

# Bash script to seed demo data

echo "🚀 Seeding McKinsey Executive Demo Data..."
echo ""

export PYTHONPATH="$(pwd)"

python scripts/generate_demo_data.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Demo data seeded successfully!"
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Start the backend: uvicorn app.main:app --reload"
    echo "   2. Start the frontend: npm run dev"
    echo "   3. Login with: demo@mckinsey.com / demo1234"
    echo ""
else
    echo ""
    echo "❌ Failed to seed demo data"
    echo "Check error messages above"
    exit 1
fi
