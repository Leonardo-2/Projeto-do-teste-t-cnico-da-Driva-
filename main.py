from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
import os
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

# Configurações
API_KEY = "driva_test_key_abc123xyz789"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://driva_user:driva_password@localhost:5432/driva_dw")

app = FastAPI(title="Driva Tech Test API")
fake = Faker('pt_BR')

# Banco de Dados
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Geração dos dados para o teste técnico
@app.on_event("startup")
def seed_database():
    try:
        with SessionLocal() as db:
            # Verifica se a tabela existe antes de consultar
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS public.api_enrichments_seed (
                    id TEXT PRIMARY KEY,
                    id_workspace TEXT,
                    workspace_name TEXT,
                    total_contacts INTEGER,
                    contact_type TEXT,
                    status TEXT,
                    created_at TIMESTAMP WITH TIME ZONE,
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            db.commit()

            result = db.execute(text("SELECT count(*) FROM public.api_enrichments_seed"))
            count = result.scalar()
            
            if count == 0:
                print("Gerando dados de teste (Seed)...")
                
                values = [] 
                
                status_opts = ["PROCESSING", "COMPLETED", "FAILED", "CANCELED"]
                type_opts = ["PERSON", "COMPANY"]
                
                for _ in range(5000):
                    created = fake.date_time_between(start_date='-6m', end_date='now')
                    updated = created + timedelta(minutes=random.randint(1, 240))
                    values.append({
                        "id": str(uuid.uuid4()),
                        "id_workspace": str(uuid.uuid4()),
                        "workspace_name": fake.company(),
                        "total_contacts": random.randint(10, 5000),
                        "contact_type": random.choice(type_opts),
                        "status": random.choices(status_opts, weights=[10, 80, 5, 5])[0],
                        "created_at": created,
                        "updated_at": updated
                    })
                
                db.execute(text("""
                    INSERT INTO public.api_enrichments_seed 
                    (id, id_workspace, workspace_name, total_contacts, contact_type, status, created_at, updated_at)
                    VALUES (:id, :id_workspace, :workspace_name, :total_contacts, :contact_type, :status, :created_at, :updated_at)
                """), values)
                db.commit()
                print("Seeding concluído.")
    except Exception as e:
        print(f"Erro no seeding: {e}")

# Geração dos Endpoints
@app.get("/people/v1/enrichments")
def get_enrichments(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Simula erro 429 
    if random.random() < 0.15:
        return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})

    offset = (page - 1) * limit
    try:
        total_items = db.execute(text("SELECT count(*) FROM public.api_enrichments_seed")).scalar()
        query = text("SELECT * FROM public.api_enrichments_seed ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
        result = db.execute(query, {"limit": limit, "offset": offset}).mappings().all()
        
        return {
            "meta": {"total_items": total_items, "total_pages": (total_items + limit - 1) // limit},
            "data": result,
            "page": page
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

# Geração das métricas para o dashboard
@app.get("/analytics/overview")
def get_analytics(db: Session = Depends(get_db)):
    try:
        kpis = db.execute(text("""
            SELECT 
                COUNT(*) as total_jobs,
                ROUND(AVG(CASE WHEN processamento_sucesso THEN 1 ELSE 0 END) * 100, 2) as taxa_sucesso,
                ROUND(AVG(duracao_processamento_minutos)::numeric, 2) as tempo_medio
            FROM warehouse.gold_enrichments
        """)).mappings().one()
        
        cats = db.execute(text("SELECT categoria_tamanho_job, COUNT(*) as count FROM warehouse.gold_enrichments GROUP BY 1")).mappings().all()
        
        return {"kpis": dict(kpis), "distribuicao": [dict(r) for r in cats]}
    except:
        return {"kpis": {"total_jobs": 0}, "distribuicao": []}

# Geração da lista paginada
@app.get("/analytics/enrichments")
def get_gold_list(limit: int = 50, db: Session = Depends(get_db)):
    try:
        res = db.execute(text("SELECT * FROM warehouse.gold_enrichments ORDER BY data_criacao DESC LIMIT :limit"), {"limit": limit}).mappings().all()
        return [dict(r) for r in res]
    except:
        return []