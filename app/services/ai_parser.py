from groq import Groq
import os
import json
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def parse_query(query: str):
    try:
        prompt = f"""
            Extract structured information from the user query.

            Return ONLY valid JSON (no explanation):

            {{
            "intent": "travel or general",
            "location": "city or place or null"
            }}

            Rules:
            - intent = "travel" if query is about trips, hotels, places, transport
            - intent = "general" otherwise
            - location = extract city/place name if present
            - if no location → null

            Query: {query}
            """
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        text = response.choices[0].message.content
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return {
            "intent": data.get("intent", "general"),
            "location": data.get("location")
        }

    except Exception as e:
        print("AI parse error:", str(e))
        return {
            "intent": "general",
            "location": None
        }