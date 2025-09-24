import openai
from .scenario import All_Scenario

class OpenAIConfig:
    def __init__(self, api_key: str = None, model: str = "gpt-4.1-mini"):
        """
        Initializes the OpenAI API configuration with the given API key and model.
        """
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key
        self.conversation_history = [{"role": "system", "content": "You are a helpful for people who are homeless. Provide concise and accurate information."}]

    def get_response(self, prompt: str, history: list, context: str = "") -> str:
        try:
            system_prompt = f"""
            You are Hope AI and you are a compassionate assistant for vulnerable individuals in Nevada, USA, providing support for homelessness, trauma, and safety.

            Core Duties:
            - Start each session with a warm greeting (e.g.: "Hi, I'm here to help. Would you like to start now or later?").
            - Handle trauma confidently and empathetically, acknowledging feelings and offering support.
            - A short, emotionally supportive message based on the user's need (e.g. hunger, shelter, hygiene).
            - Redirect outside of your scope with gentle fallbacks.
            - Prioritize safety, emotional well-being, and empowering the user to guide the conversation.

            Conversation Style:
            - Be concise, empathetic, safety-focused and use trauma-sensitive language.
            - Avoid overwhelming responses; ask for permission to provide more detail.
            - If the request is outside your scope, offer a gentle fallback: â€œThis sounds like something else might handle. Should I guide you there?â€
            - Your goal is to help people in need.

            Contextual Data:
            {context}

            Scenarios to follow:
            1. {All_Scenario.shelter}
            2. {All_Scenario.medical}
            3. {All_Scenario.hygiene}
            4. {All_Scenario.suggestions}
            5. {All_Scenario.scenario1}
            6. {All_Scenario.scenario2}
            """

            api_history = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": prompt}]

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=api_history
            )

            reply = response.choices[0].message['content']
            return reply
        except Exception as e:
            print(f"Error communicating with OpenAI API: {e}")
            return "Sorry, I couldn't process your request at the moment. Please try again later."

    

    def get_history(self):
        return self.conversation_history