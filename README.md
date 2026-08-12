# Íris API

Backend acadêmico/mock para a **Íris**, assistente virtual de saúde do TCC.

> **Importante:** o projeto deve usar somente dados fictícios. Ele não acessa dados reais do SUS, CadSUS ou RNDS.

## Arquitetura

```text
Weni / Íris
    |
    | HTTPS
    v
FastAPI (Render)
    |
    v
Supabase / PostgreSQL
```

## Funcionalidades incluídas

- Identificação de paciente por CNS
- OTP simulado
- JWT de sessão
- Perfil do paciente
- Listagem/agendamento/remarcação/cancelamento de consultas
- Horários disponíveis
- Exames e resultados
- Vacinas e pendências
- Busca de medicamentos
- Estoque por unidade
- Unidades de saúde
- Histórico consolidado

## 1. Criar banco no Supabase

1. Crie um projeto no Supabase.
2. Abra o **SQL Editor**.
3. Execute `sql/schema.sql`.
4. Depois execute `sql/seed.sql`.
5. Em **Project Settings > API**, copie:
   - Project URL
   - `service_role` key

Nunca coloque a `service_role` diretamente na Weni ou em código frontend. Ela deve ficar apenas como variável de ambiente do backend.

## 2. Variáveis de ambiente

Copie:

```bash
cp .env.example .env
```

Preencha:

```env
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
JWT_SECRET=...
```

Para desenvolvimento:

```env
DEV_OTP_CODE=123456
RETURN_DEV_OTP=true
```

## 3. Rodar localmente

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instale:

```bash
pip install -r requirements.txt
```

Execute:

```bash
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## 4. Teste inicial

### Localizar paciente

`POST /patients/lookup`

```json
{
  "cns": "123456789012345"
}
```

### Solicitar OTP

Use o `patient.id` recebido:

`POST /auth/otp/request`

```json
{
  "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
}
```

Em desenvolvimento, a resposta contém:

```json
{
  "dev_code": "123456"
}
```

### Validar OTP

`POST /auth/otp/verify`

```json
{
  "challenge_id": "ID_RECEBIDO_NO_PASSO_ANTERIOR",
  "code": "123456"
}
```

Guarde o `access_token`.

Para os endpoints protegidos, envie:

```http
Authorization: Bearer SEU_ACCESS_TOKEN
```

## 5. Endpoints

### Públicos

- `GET /health`
- `POST /patients/lookup`
- `POST /auth/otp/request`
- `POST /auth/otp/verify`

### Autenticados

- `GET /patients/me`
- `GET /appointments`
- `GET /appointments/availability`
- `POST /appointments`
- `PATCH /appointments/{id}`
- `DELETE /appointments/{id}`
- `GET /exams`
- `GET /exams/{id}/result`
- `GET /vaccines`
- `GET /vaccines/pending`
- `GET /medications/search?name=losartana`
- `GET /medications/{id}/availability`
- `GET /health-units`
- `GET /history`

## 6. Deploy no Render

Crie um **Web Service** conectado ao repositório GitHub.

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Adicione no Render as variáveis:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `JWT_SECRET`
- `JWT_ALGORITHM=HS256`
- `JWT_EXPIRE_MINUTES=30`
- `OTP_EXPIRE_MINUTES=5`
- `DEV_OTP_CODE=123456`
- `RETURN_DEV_OTP=true`

Depois do deploy, a Weni poderá consumir URLs como:

```text
https://SEU-SERVICO.onrender.com/patients/lookup
```

## Dados de teste

Paciente 1:

```text
CNS: 123456789012345
Nome: Maria da Silva
OTP: 123456
```

Paciente 2:

```text
CNS: 987654321098765
Nome: João Oliveira
OTP: 123456
```

Todos são fictícios.
