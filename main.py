from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END

from agents.retriever_agent import RetrieverAgent
from agents.summarizer_agent import SummarizerAgent
from agents.answer_agent import AnswerAgent
from utils.logger import logging


class WorkflowState(TypedDict, total=False):
    question: str
    context: str
    summary: str
    answer: str


def build_graph():
    retriever = RetrieverAgent()
    summarizer = SummarizerAgent()
    answer = AnswerAgent()

    graph = StateGraph(WorkflowState)
    graph.add_node("retrieve", retriever.execute)
    graph.add_node("summarize", summarizer.execute)
    graph.add_node("answer", answer.execute)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "summarize")
    graph.add_edge("summarize", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


if __name__ == "__main__":
    try:
        app = build_graph()
        question = input("Ask a question: ")
        result = app.invoke({"question": question})
        print("\n✅ Final Answer:\n", result.get("answer"))
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        logging.error(f"Workflow failed: {e}", exc_info=True)
