from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.embeddings.ollama import OllamaEmbedding
from src.core.chatbotLaptopRecommenderClass import chatbotLaptopRecommender
from src.ui.interface import Interface
from llama_index.llms.groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

# === Conexión con la base de datos. ===
graph_connection = Neo4jGraphStore(
    username=os.environ["NEO4J_USER"],
    password=os.environ["NEO4J_PASSWORD"],
    url=os.environ["NEO4J_URI"],
    database=os.environ["NEO4J_DATABASE"],
    refresh_schema=False
)

# === Modelo LLM de Groq ===
llm = Groq(
        model= os.environ.get("LLM_MODEL"),
        api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.2,
        max_tokens=4000,
    )

# === Modelo de Embedding de Ollama ===
embedding_model = OllamaEmbedding(model_name=os.environ["EMBEDDING_MODEL"])


# === Función principal ===
def main():
    chatbot = chatbotLaptopRecommender(graph_connection, llm, embedding_model)
    interfaz = Interface(chatbot)
    interfaz.render()

if __name__ == "__main__":
    main()
