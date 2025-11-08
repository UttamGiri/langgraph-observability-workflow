from agents.base_agent import BaseAgent


class AnswerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AnswerAgent")

    def execute(self, inputs):
        summary = inputs.get("summary")
        question = inputs.get("question")

        if summary is None:
            raise ValueError("Expected 'summary' in workflow state before answering.")
        if question is None:
            raise ValueError("Expected 'question' in workflow state before answering.")

        prompt = f"Context Summary:\n{summary}\n\nQuestion: {question}"
        answer = self.run(prompt, inputs)
        return {"answer": answer}
