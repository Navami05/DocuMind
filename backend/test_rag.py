import requests


print("\n==============================")
print("          RAG TEST")
print("==============================")


query = "What are the limitations of the existing SPMR systems?"


response = requests.post(
    "http://127.0.0.1:8000/search",
    params={
        "query": query
    }
)


print("\nStatus Code:")
print(response.status_code)


if response.status_code == 200:

    data = response.json()

    print("\n==============================")
    print("            ANSWER")
    print("==============================")

    print(data["answer"])


    print("\n==============================")
    print("        SOURCES USED")
    print("==============================")

    for index, result in enumerate(
        data["results"],
        start=1
    ):

        print(f"\n--- Source {index} ---")

        print(
            "Page:",
            result["page"]
        )

        print(
            "Section:",
            result["section"]
        )

        print(
            "Rerank Score:",
            result["rerank_score"]
        )

else:

    print("\nERROR:")

    print(response.text)