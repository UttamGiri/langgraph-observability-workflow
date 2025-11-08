from agents.base_agent import BaseAgent


class RetrieverAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="RetrieverAgent")

    def execute(self, inputs):
        with open("data/context.txt", "r", encoding="utf-8") as f:
            context = f.read()
        return {"context": context}
