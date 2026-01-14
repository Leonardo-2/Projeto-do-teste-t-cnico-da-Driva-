SET timezone TO 'America/Sao_Paulo';
CREATE SCHEMA IF NOT EXISTS warehouse;

-- BRONZE
CREATE TABLE IF NOT EXISTS warehouse.bronze_enrichments (
    id TEXT PRIMARY KEY,
    raw_data JSONB NOT NULL,
    dw_ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    dw_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- GOLD
CREATE TABLE IF NOT EXISTS warehouse.gold_enrichments (
    id_enriquecimento TEXT PRIMARY KEY,
    id_workspace TEXT NOT NULL,
    nome_workspace TEXT,
    total_contatos INTEGER,
    tipo_contato TEXT,
    status_processamento TEXT,
    data_criacao TIMESTAMP WITH TIME ZONE,
    data_atualizacao TIMESTAMP WITH TIME ZONE,
    duracao_processamento_minutos FLOAT,
    tempo_por_contato_minutos FLOAT,
    processamento_sucesso BOOLEAN,
    categoria_tamanho_job TEXT,
    necessita_reprocessamento BOOLEAN,
    data_atualizacao_dw TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- FONTE DA API
CREATE TABLE IF NOT EXISTS public.api_enrichments_seed (
    id TEXT PRIMARY KEY,
    id_workspace TEXT,
    workspace_name TEXT,
    total_contacts INTEGER,
    contact_type TEXT,
    status TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.dw_updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_bronze_modtime
    BEFORE UPDATE ON warehouse.bronze_enrichments
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();