import agent


def calculatrice(expression):
    return eval(expression)


print(
calculatrice("5+5")
)

print(
calculatrice("20*5")
)
print(
calculatrice("100/4")
)

def calculatrice_node(state):
    question = state["question"]
    resultat = calculatrice(
    question
    )
    state["reponse"] = str(
    resultat
    )
    return state

def decision_node(state):
    question = state["question"]
    if "bonjour" in question.lower():
        state["type_question"] = (
        "salutation"
        )
    elif (
        "+" in question
        or "-" in question
        or "*" in question
        or "/" in question
        ):
        state["type_question"] = (
        "calcul"
    )
    else:
        state["type_question"] = (
        "documentation"
        )
        return state

resultat = agent.invoke(
{"question": "5+5"}
)    
print(resultat)

resultat = agent.invoke(
{"question": "50*4"}
)
print(resultat)

resultat = agent.invoke(
{"question": "100/2"}
)
print(resultat)
print(
resultat["reponse"]
)