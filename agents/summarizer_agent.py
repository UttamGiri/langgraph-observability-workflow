from agents.base_agent import BaseAgent


class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="SummarizerAgent")

    def execute(self, inputs):
        context = inputs.get("context")
        if context is None:
            raise ValueError("Expected 'context' in workflow state before summarization.")

        prompt = f"Summarize the following text:\n\n{context}"
        summary = self.run(prompt, inputs)
        return {"summary": summary}
