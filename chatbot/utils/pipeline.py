from .file_uploder import file_uploder
from .prompt import OpenAIConfig
 
class HopePipeline:
    def __init__(self, api_key):
        self.openai = OpenAIConfig(api_key=api_key)
 
    def run(self, user_input, location, csv_data, history):
        enriched_input = user_input
        if location:
            enriched_input += f"\n\n[User is currently located at: {location}]"
 
        context = ""
        keywords = file_uploder.extract_keywords(user_input)
 
        if csv_data is not None and keywords:
            filtered_df = file_uploder.filter_by_keywords(csv_data, keywords)
            if not filtered_df.empty:
                chunks = file_uploder.chunk_dataframe(filtered_df)
                context = chunks[0]
 
        prompt = self.build_prompt(enriched_input, context)
 
        response = self.openai.get_response(prompt, history, context)
 
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})
 
        return response
 
    def build_prompt(self, enriched_input, context):
        if context:
            return f"""
                    User said: {enriched_input}
 
                    Please respond with:
                    1. A short, emotionally supportive suggestion that acknowledges the user's need.
                    2. Then suggest 1 to 3 nearby resources using the data provided below. Include name and Google Maps link if available.
                    3. Keep your tone warm, respectful, and easy to understand. If the user seems overwhelmed, offer to break things down or follow up gently.
 
                    Data:
                    {context}
                    """
        else:
            return f"""
                    User said: {enriched_input}
 
                    Please respond with:
                    - Don't need to be overly robotic, verbose and emotional; keep responses concise and focused.
                    - Don't say that "I'm sorry to hear that" repeatedly; be empathetic but avoid clichés.
                    - Prioritize safety, emotional well-being, and empower the user to guide the conversation.
                    - Redirect outside of your scope with gentle fallbacks.
                    - If the request is outside your scope, offer a gentle fallback.
                    - If the user asks for suggestions or general advice, provide practical suggestions or resources related to homelessness, trauma, or safety.
                    - Your goal is to help needy people.
                    - If no data is available, gently ask if the user would like to expand the search or clarify their request.
 
                    """
 