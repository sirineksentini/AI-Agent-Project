from datetime import time
from typing import TypedDict
from langgraph.graph import StateGraph, END
from pypdf import PdfReader
from docx import Document
import requests

question: str = ""


class AgentState(TypedDict):
    question: str
    reponse: str
    type_question: str


def analyse_node(state):
    question = state["question"]
    print("[LOG] Question reçue :", question)
    return state


def reponse_node(state):
    question = state["question"]
    state["reponse"] = f"Votre question est : {question}"
    return state


def decision_node(state):
    question = state["question"].lower()
    if "bonjour" in question:
        state["type_question"] = "salutation"
    elif "+" in question or "-" in question or "*" in question or "/" in question:
        state["type_question"] = "calcul"
    elif ".pdf" in question:
        state["type_question"] = "pdf"
    elif ".docx" in question:
        state["type_question"] = "docx"
    elif ".txt" in question:
        state["type_question"] = "txt"
    elif ".txt" == str:
        state["type_question"] = "documentation"
    else:
        "[LOG] Outil sélectionné :",
    state["type_question"]
    return state


def calculatrice_node(state):
    question = state["question"]
    resultat = calculatrice(question)
    state["reponse"] = str(resultat)
    return state


def calculatrice(expression):
    return eval(expression)


def documentation_node(state):
    question = state["question"]
    prompt = f"""
    Historique :{historique}
    Question :{question}
    Réponse :
    """
    reponse = llm_local(prompt)
    state["reponse"] = reponse
    return state


def greeting_node(state):
    state["reponse"] = "Bonjour ! Comment puis-je vous aider ?"
    return state


def txt_reader(chemin_fichier):
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as fichier:
            return fichier.read()
    except:
        return "Fichier introuvable."


def pdf_reader(chemin_fichier):
    try:
        lecteur = PdfReader(chemin_fichier)
        contenu = ""
        for page in lecteur.pages:
            contenu += page.extract_text()
        return contenu
    except:
        return "Fichier introuvable."


def docx_reader(chemin_fichier):
    try:
        doc = Document(chemin_fichier)
        contenu = ""
        for paragraphe in doc.paragraphs:
            contenu += paragraphe.text + "\n"
        return contenu
    except:
        return "Fichier introuvable."


def llm_local(prompt):
    url = "http://localhost:11434/api/generate"
    data = {"model": "mistral", "prompt": prompt, "stream": False}
    response = requests.post(url, json=data)
    return response.json()["response"]


def route_question(state):
    return state["type_question"]


def txt_reader_node(state):
    contenu = txt_reader("documents/rh.txt")
    question = state["question"]
    prompt = f"""
    Historique :{historique}
    Contexte :{contenu}
    Question :{question}
    Réponse :
    """
    state["reponse"] = llm_local(prompt)
    return state


def pdf_reader_node(state):
    contenu = pdf_reader("documents/formation.pdf")
    question = state["question"]
    prompt = f"""
    Historique :{historique}
    Contexte :{contenu}
    Question :{question}
    Réponse :
    """
    state["reponse"] = llm_local(prompt)
    return state


def docx_reader_node(state):
    contenu = docx_reader("documents/procedure.docx")
    question = state["question"]

    prompt = f"""
    Historique :{historique}
    Contexte :{contenu}
    Question :{question}
    Réponse :
    """
    state["reponse"] = llm_local(prompt)
    return state


workflow = StateGraph(AgentState)
workflow.add_node("analyse", analyse_node)
workflow.add_node("reponse", reponse_node)
workflow.add_node("salutation", greeting_node)
workflow.add_node("decision", decision_node)
workflow.add_node("calculatrice", calculatrice_node)
workflow.add_node("documentation", documentation_node)
workflow.add_node("txt_reader", txt_reader_node)
workflow.add_node("pdf_reader", pdf_reader_node)
workflow.add_node("docx_reader", docx_reader_node)


workflow.add_conditional_edges(
    "decision",
    route_question,
    {
        "calcul": "calculatrice",
        "pdf": "pdf_reader",
        "docx": "docx_reader",
        "txt": "txt_reader",
        "documentation": "documentation",
    },
)

workflow.set_entry_point("analyse")

workflow.add_edge("analyse", "decision")

workflow.add_edge("documentation", END)

workflow.add_edge("calculatrice", END)

workflow.add_edge("salutation", END)
workflow.add_edge("txt_reader", END)
workflow.add_edge("pdf_reader", END)
workflow.add_edge("docx_reader", END)

agent = workflow.compile()
memoire = []
historique = "\n".join(memoire)
if question == "":
    print("Veuillez saisir une question.")
# resultat = agent.invoke({"question":"Combien font 5+5 ?"})
# resultat = agent.invoke({"question":"Quels sont les congés ?"})
# resultat = agent.invoke({"question":"Combien font cinq plus trois ?"})
# resultat = agent.invoke({"question":"Bonjour, comment vas-tu ?"})
# print(calculatrice("100/4"))
# resultat = agent.invoke({"question": "5+5"})
# resultat = agent.invoke({"question": "50*4"})
# resultat = agent.invoke({"question": "100/2"})
# print(resultat)
# resultat = agent.invoke({"question": "Lis le fichier RH "})
# print(txt_reader("documents/rh.txt"))
# print(resultat["reponse"])
# print(pdf_reader("documents/formation.pdf"))
# print(docx_reader("documents/procedure.docx"))
# resultat = agent.invoke({"question": "50+25"})
# resultat = agent.invoke({"question": "Lis formation.pdf"})
# resultat = agent.invoke({"question": "Lis procedure.docx"})
# resultat = agent.invoke({"question": "Lis rh.txt"})
# print(resultat["reponse"])
print(llm_local("Bonjour"))
# resultat = agent.invoke({"question": "Qu'est-ce qu'un Agent IA ?"})
# resultat = agent.invoke({"question": "Lis formation.pdf"})
# resultat = agent.invoke({"question": "Quels sujets sont étudiés ?"})
# resultat = agent.invoke({"question": "Lis procedure.docx"})
# resultat = agent.invoke({"question": "Que dit la procédure RH ?"})
debut = time.time()
resultat = agent.invoke({"question": question})
fin = time.time()
print("Temps :", fin - debut, "secondes")
print("[LOG] Réponse générée")
print(resultat["reponse"])
memoire.append(f"Utilisateur : {question}")
memoire.append(f"Assistant : {reponse}")
questions = [
    "Quels sont les congés ?",
    "Lis formation.pdf",
    "50+20",
    "Lis procedure.docx",
]
memoire = []
for question in questions:
    if question == "":
        print("Veuillez saisir une question.")
        continue
    historique = "\n".join(memoire)
    debut = time.time()
    resultat = agent.invoke({"question": question})
    fin = time.time()
    reponse = resultat["reponse"]
    memoire.append(f"Utilisateur : {question}")
    memoire.append(f"Assistant : {reponse}")
    print(reponse)
    print("[LOG] Réponse générée")
    print("Temps :", fin - debut, "secondes")
    print("-------------")
