import json
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_structured_response(query: str, context: str):
    try:
        prompt = f"""
        You are a professional travel planner.
        Using the context below, generate a clean structured JSON response.
        Context:
        {context}
        User Query:
        {query}
        STRICT RULES:
        - Return ONLY valid JSON
        - No broken text
        - No extra explanation
        - Structure must match:
        {{
        "summary": "...",
        "places": [
            {{
            "city": "...",
            "place": "...",
            "category": "...",
            "hotels": {{
                "5_star": "...",
                "3_star": "...",
                "budget": "..."
            }},
            "restaurants": ["...", "..."]
            }}
        ],
        "transport": {{
            "flight": "...",
            "train": "...",
            "bus": "..."
        }},
        "budget": "...",
        "tips": "..."
        }}
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        text = response.choices[0].message.content

        try:
            return json.loads(text)
        except:
            return {
                "summary": "Unable to generate structured response",
                "places": [],
                "transport": {},
                "budget": "",
                "tips": "Try again"
            }
    except Exception as e:
        return {
            "summary": "Error generating response",
            "places": [],
            "transport": {},
            "budget": "",
            "tips": "Try again"
        }

def humanize_response(data: dict):
    try:
        prompt = f"""
        You are a professional travel assistant.
        Convert the following JSON into a friendly, human-like travel explanation.
        Rules:
        - Explain like a human (not robotic)
        - Use simple paragraphs
        - Highlight important points (places, budget, tips)
        - Make it engaging and easy to read
        - DO NOT output JSON
        - DO NOT repeat keys like "summary", "places"
        - Format nicely with headings and spacing
        JSON:
        {data}
        """
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        return response.choices[0].message.content
    except Exception as e:
        return {
            "summary": "Error generating response",
            "places": [],
            "transport": {},
            "budget": "",
            "tips": "Try again"
        }