from proj_llm_agent import LLM_Agent


class EducationAgent(LLM_Agent):
    def __init__(self):
        super().__init__("Summary Agent", self.system_instructions, response_mime_type="application/json")
