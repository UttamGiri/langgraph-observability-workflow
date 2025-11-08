import os
import socket
import time

from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_openai import ChatOpenAI

from utils.logger import log_step, logging

# --- OpenTelemetry setup ---
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


load_dotenv()


# Configure Jaeger exporter
service_name = os.getenv("OTEL_SERVICE_NAME", "langgraph-observability")


def _resolve_jaeger_host():
    configured_host = os.getenv("JAEGER_AGENT_HOST")
    if configured_host:
        return configured_host

    for candidate in ("host.docker.internal", "localhost"):
        try:
            socket.gethostbyname(candidate)
            return candidate
        except socket.gaierror:
            continue

    return "localhost"


jaeger_host = _resolve_jaeger_host()
jaeger_port = int(os.getenv("JAEGER_AGENT_PORT", "6831"))

resource = Resource.create({SERVICE_NAME: service_name})

provider = TracerProvider(resource=resource)
jaeger_exporter = JaegerExporter(
    agent_host_name=jaeger_host,
    agent_port=jaeger_port,
)
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)


class BaseAgent:
    def __init__(self, name, model="gpt-4o-mini", temperature=0.1):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required but was not found. Set it in the environment or .env file.")

        logging.info(
            "Initializing '%s' with Jaeger exporter targeting %s:%s (service=%s)",
            name,
            jaeger_host,
            jaeger_port,
            service_name,
        )

        self.name = name
        self.llm = ChatOpenAI(model=model, temperature=temperature, api_key=api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8))
    def run(self, prompt, inputs=None):
        """Run LLM call within an OpenTelemetry span"""
        with tracer.start_as_current_span(self.name) as span:
            start = time.time()
            response = self.llm.invoke(prompt)
            duration = round(time.time() - start, 2)

            outputs = {"response": response.content, "duration_sec": duration}
            # Add tracing metadata
            span.set_attribute("model", "gpt-4o-mini")
            span.set_attribute("duration_sec", duration)
            span.set_attribute("prompt_length", len(prompt))
            span.set_attribute("response_length", len(response.content))
            log_step(self.name, inputs or {}, outputs)
            return outputs["response"]
