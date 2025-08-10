# Agno Agente de Preço de Ações

Um pequeno serviço **FastAPI** que utiliza o framework **Agno** com um modelo **Ollama** para buscar preços de ações via a ferramenta `YFinanceTools`.

---

## Pré‑requisitos

- **Docker** e **Docker Compose** instalados na sua máquina.
- Um servidor **Ollama** rodando localmente (endereço padrão `http://host.docker.internal:11434`).
- Uma chave de API da **OpenAI** (necessária pelo pacote Agno mesmo ao usar Ollama).

## Configuração

1. **Clone o repositório**
   ```bash
   git clone https://github.com/fsmalaquias/estudo-agno-ai.git
   cd estudo-agno-ai
   ```

2. **Crie o arquivo `.env`** (já presente no repositório) com as variáveis necessárias:
   ```dotenv
   OPENAI_API_KEY=sua‑chave‑openai
   OLLAMA_HOST=http://host.docker.internal:11434
   ```
   *O arquivo `.env` está incluído no `.gitignore` e não será versionado.*

3. **Construa e inicie os containers**
   ```bash
   docker compose up -d --build
   ```
   O serviço ficará disponível em **http://localhost:8000**. O container executa o `uvicorn` com a flag `--reload`, portanto qualquer alteração no código fonte será recarregada automaticamente.

## Uso da API

O serviço expõe um único endpoint:

- **POST** `/query`
  - **Corpo da requisição** (JSON): `{ "question": "<sua pergunta>" }`
  - **Resposta** (JSON): `{ "answer": "<resultado>" }`

### Exemplo de requisição com `curl`
```bash
curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question":"Qual o preço da ação da Apple?"}'
```

A resposta será um JSON limpo, por exemplo:
```json
{ "answer": "229.35" }
```

Se o modelo LLM retornar um objeto de erro, a API encaminhará o código de status HTTP e a mensagem apropriados.

---

## Notas de desenvolvimento

- O modelo LLM está configurado em `api.py` usando `Ollama(id="llama3.2")`. Altere o ID do modelo caso queira usar outro modelo Ollama.
- A função auxiliar `clean_answer` remove fences de markdown, crases e quebras de linha antes de analisar a resposta.
- As variáveis de ambiente são carregadas a partir do arquivo `.env` via Docker Compose (`env_file:`). Nenhum segredo está hard‑coded no Dockerfile.

Divirta‑se desenvolvendo com **Agno**! 🚀
