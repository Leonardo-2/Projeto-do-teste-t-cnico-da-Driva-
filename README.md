# Projeto-do-teste-t-cnico-da-Driva-
Projeto do teste técnico da Driva, pipeline de dados 


Olá! Esse repositório contém a minha solução para o desafio de Engenharia de Dados da Driva. Basicamente, eu construí um pipeline completo que pega dados brutos de uma API, guarda num banco de dados, limpa esses dados e mostra tudo num painel (dashboard).

Aprendi a como conectar várias ferramentas usando Docker.

1. Visão Geral da Solução
A ideia principal aqui foi criar uma arquitetura de Data Warehouse separada em duas camadas: Bronze (dados brutos) e Gold (dados limpos e prontos para análise).

Utilizei o Docker para empacotar os containers, sem a necessidade da instalação de outros aplicativos.

Sugiro a instalação local do aplicativo Docker Windows (se o Sistema Operacional for Windows)

As ferramentas que utilizadas foram:

PostgreSQL: O banco de dados onde armazeno as tabelas Bronze e Gold.

n8n: Uma ferramenta visual que busca os dados da API a cada 5 minutos e salva no banco.

API (Python/FastAPI): Eu criei essa API para utilizar em duas etapas: primeiro para se adaptar como uma fonte dos dados (gerando dados falsos) e também repassar os dados prontos para o dashboard.

Dashboard (Streamlit): É a resultado gráfico final onde se pode observar os gráficos e as tabelas com os resultados.

2. Como Subir o Ambiente
Para rodar o projeto, você só precisa ter o Docker e o Docker Compose instalados.

Clone este repositório (ou baixe a pasta).

Abra o terminal dentro da pasta principal (onde está o arquivo docker-compose.yml).

Rode o comando: docker-compose up --build -d

O resultado esperado é a ferramenta Docker baixar as imagens e subir 4 containers para a API.

Observação: Para a conferência se está tudo rodando corretamente utilize o comando: docker ps.

3. Como Rodar o Frontend (Dashboard)
   
O Frontend está armazenado/implementado dentro do Docker. Com isso, ao rodar o passo anterior, o dashboard já está funcionando.

Acesse no navegador: http://localhost:8501 

Se por algum motivo você quiser rodar fora do Docker (para testar código novo, por exemplo), você precisaria ter Python instalado e rodar o comando abaixo: 

cd dashboard
pip install -r requirements.txt
streamlit run app.py

4. Como Importar/Executar Workflows (n8n)

A ferramenta n8n extrai o dado bruto e transporta para o banco de dados referido.

O próximo passo é acessar o n8n em: http://localhost:5678, criar um usuário e senha e configurar a credencial do banco de dados (Credential):

Host: postgres 

Observação: Não utilizar localhost, porque dentro do Docker o nome é postgres.

Database: driva_dw

User: driva_user

Password: driva_password

Port: 5432

Criar os Workflows: Eu sugiro dois fluxos principais:

Ingestão (Bronze): Usa um nó HTTP Request para ajustar a configuração da API (http://api:3000/people/v1/enrichments) e um nó Postgres para salvar na tabela warehouse.bronze_enrichments.

Processamento (Gold): Realizar a leitura da Bronze, usa um nó de Code (JavaScript) para traduzir os status (ex: "COMPLETED" vira "CONCLUIDO") e calcular métricas, e salva na warehouse.gold_enrichments.

Observação: Para ativar a automação, é só ativar o workflow que tem o nó "Schedule" configurado para rodar a cada 5 minutos.

5. Exemplos de Chamadas para os Endpoints

A API que eu construida roda na porta 3000. Ela necessita de uma chave de segurança (Token) para funcionar.

Chave de API (Token): Bearer driva_test_key_abc123xyz789.

Aqui estão exemplos de como testar usando o terminal (cURL):

1. Ver dados da Fonte (Simulação de Enriquecimentos): Esse endpoint traz os dados paginados.

curl -X GET "http://localhost:3000/people/v1/enrichments?page=1&limit=10" \
     -H "Authorization: Bearer driva_test_key_abc123xyz789"

2. Ver dados Analíticos (Resumo para o Dashboard): Esse endpoint traz os KPIs que aparecem no topo do dashboard.

curl -X GET "http://localhost:3000/analytics/overview" \
     -H "Authorization: Bearer driva_test_key_abc123xyz789"


Projeto desenvolvido como parte do processo seletivo da Driva. Aprendi bastante sobre Docker, volumes e redes durante o processo.
