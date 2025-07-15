
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import os

llm = ChatGoogleGenerativeAI(model='models/gemini-1.5-flash-latest', temperature=0.2)

def build_graph():
    def get_symptom(state: dict) -> dict:
        state["symptom"] = state.get("user_input", "")
        return state

    def classify_symptom(state: dict) -> dict:
        prompt = (
            "You are a helpful medical assistant. Classify the symptom below:\n"
            "- General\n- Emergency\n- Mental Health\n"
            f"Symptom: {state['symptom']}\n"
            "Respond with only one word: General, Emergency or Mental Health."
        )
        response = llm([HumanMessage(content=prompt)])
        state["category"] = response.content.strip()
        return state

    def symptom_router(state: dict) -> str:
        return state["category"].lower()

    def general_response(state: dict) -> dict:
        state["answer"] = f"{state['symptom']} → General: redirecting to general ward."
        return state

    def mental_health_response(state: dict) -> dict:
        state["answer"] = f"{state['symptom']} → Mental Health: redirecting to therapy ward."
        return state

    def emergency_response(state: dict) -> dict:
        state["answer"] = f"{state['symptom']} → Emergency: immediate care required."
        return state

    builder = StateGraph(dict)
    builder.set_entry_point("get_symptom")
    builder.add_node("get_symptom", get_symptom)
    builder.add_node("classify_symptom", classify_symptom)
    builder.add_node("general", general_response)
    builder.add_node("mental health", mental_health_response)
    builder.add_node("emergency", emergency_response)

    builder.add_edge("get_symptom", "classify_symptom")
    builder.add_conditional_edges("classify_symptom", symptom_router, {
        "general": "general",
        "mental health": "mental health",
        "emergency": "emergency"
    })
    builder.add_edge("general", END)
    builder.add_edge("mental health", END)
    builder.add_edge("emergency", END)

    return builder.compile()
