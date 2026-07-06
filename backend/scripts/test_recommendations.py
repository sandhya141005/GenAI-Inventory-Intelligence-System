import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.services.analytics_service import AnalyticsService

db = SessionLocal()
service = AnalyticsService(db)
result = service.recommendations()
recs = result["recommendations"]

print(f"\n✅ Generated {len(recs)} recommendations\n")

rec_types = {}
for r in recs:
    rec_type = r['title'].split(':')[0].strip()
    rec_types[rec_type] = rec_types.get(rec_type, 0) + 1

print("📊 Recommendation Types Distribution:")
for rec_type, count in sorted(rec_types.items(), key=lambda x: -x[1]):
    print(f"   {rec_type:30} {count:3} ({count/len(recs)*100:5.1f}%)")

print(f"\n🎯 Unique recommendation types: {len(rec_types)}")
print(f"✨ Diversity Score: {len(rec_types)/len(recs)*100:.1f}%")

print("\n📋 Sample Recommendations:")
for i, rec in enumerate(recs[:5], 1):
    print(f"\n{i}. {rec['title']}")
    print(f"   Priority: {rec['priority']} | Confidence: {rec['confidence']}%")
    print(f"   Reason: {rec['reason'][:80]}...")
    print(f"   Action: {rec['primaryAction']}")

db.close()
