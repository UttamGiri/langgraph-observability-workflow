# LangGraph Observability Workflow

This project demonstrates a simple LangGraph workflow with OpenTelemetry tracing and structured logging. The workflow retrieves context, summarizes it, and answers a question using an LLM backed by LangChain.

## Project Structure

```
.
├── main.py
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── retriever_agent.py
│   ├── summarizer_agent.py
│   └── answer_agent.py
├── utils/
│   ├── __init__.py
│   └── logger.py
├── data/
│   └── context.txt
├── logs/
├── requirements.txt
├── Dockerfile
├── .env
└── README.md
```

## Getting Started

1. **Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenAI credentials**

   - Create a `.env` file next to `main.py` with:

     ```bash
     echo "OPENAI_API_KEY=your-openai-key" > .env
     ```

     or export the variable in your shell:

     ```bash
     export OPENAI_API_KEY=your-openai-key
     ```

4. **Run a Jaeger agent**

    - Ensure Jaeger listens on `localhost:6831` (for example: `docker run -d --name jaeger -p 6831:6831/udp -p 16686:16686 jaegertracing/all-in-one`).

5. **Execute the workflow**

   ```bash
   python main.py
   ```

   Enter a question when prompted; the final answer prints to the console.

6. **Inspect observability data**

   - Logs: view `logs/langgraph_run.log`.
   - Traces: open `http://localhost:16686` and search for spans from `RetrieverAgent`, `SummarizerAgent`, or `AnswerAgent`.

## Docker

Build and run the container locally:


Using `--network host` lets the container reach a Jaeger agent on `localhost:6831`. On macOS or Windows (Docker Desktop), map the UDP port instead:

```bash
  docker run --rm -it \
    --env-file .env \
    langgraph-observability-workflow

      docker run --rm -it \
         --env OTEL_SERVICE_NAME=langgraph-observability \
         --env JAEGER_AGENT_HOST=host.docker.internal \
         langgraph-observability-workflow

### What to provide during `docker run`

1. **Environment file**  
   - Ensure `.env` sits in your working directory before running the container.  
   - Required keys:  
     - `OPENAI_API_KEY=<your-api-key>`  
     - *(optional but recommended for Jaeger UI clarity)* `OTEL_SERVICE_NAME=langgraph-observability`
     - *(optional)* `JAEGER_AGENT_HOST=custom-host` — the app will fall back to `host.docker.internal` (for Docker Desktop) or `localhost` automatically.

   Example `.env`:

   ```bash
   OPENAI_API_KEY=sk-...             # required
   OTEL_SERVICE_NAME=langgraph-observability
   # JAEGER_AGENT_HOST=host.docker.internal
   # JAEGER_AGENT_PORT=6831
   ```

2. **Jaeger availability**  
   - Start Jaeger before launching the workflow (see commands below).  
   - If you previously created a `jaeger` container, reuse it with `docker start jaeger` to avoid name conflicts.

3. **User prompt inside the container**  
   - Once the container starts, it mirrors `python main.py` and waits for user input.  
   - Type your question at the prompt and press Enter. Example: `What are the key themes in the context?`

### Expected results

- **Console output**  
  - The final LLM answer prints to stdout with a ✅ marker.  
  - Errors surface with ❌ and also go to the logs.

- **Logs**  
  - Structured JSON logs are written to `/app/logs/langgraph_run.log` inside the container.  
  - Use `docker logs` or mount `./logs` as a volume (optional) to inspect them from the host.

- **Traces**  
  - Jaeger UI at `http://localhost:16686` shows spans under the service name you configured via `OTEL_SERVICE_NAME` (defaults to `langgraph-observability`).  
  - Search for that service; each trace lists the `RetrieverAgent`, `SummarizerAgent`, and `AnswerAgent` spans with timing and prompt/response metadata.

## Tracing

If you need to run Jaeger locally with the newer OTLP collectors enabled, use:

```bash
   docker stop jaeger && docker rm jaeger
   docker run -d --name jaeger \
     -p 16686:16686 \
     -p 6831:6831/udp \
     -p 4317:4317 \
     -p 4318:4318 \
     jaegertracing/all-in-one:1.47
```



Each agent run is wrapped in an OpenTelemetry span with metadata such as duration and prompt/response lengths. Use the Jaeger UI (`http://localhost:16686`) to inspect the traces.


# langgraph-observability-workflow
