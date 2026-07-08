import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import create_app


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_app(db_session):
    app = create_app()
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture
def mock_llm_response():
    return """
**Inventory Health Analysis**

Revenue at risk is INR 45,000 across 3 stockout-risk positions.

**Key Findings**
- **Critical Stock Levels:** 3 products below safety stock
- **Revenue Impact:** INR 45,000 at immediate risk
- **Overstock Situation:** 2 warehouses with excess inventory

**Recommended Actions**
1. **Urgent Replenishment:** Prioritize SKU-001, SKU-002 → Protect INR 30,000 revenue
2. **Transfer Optimization:** Move excess from Warehouse A to Store B

**Confidence Level**
**High** - Based on: Overview, Inventory Analysis

**Based on:** Overview, Inventory Analysis
"""
