# 💻 Guía de Usuario: Sistema de Recomendación de Portátiles

Este proyecto es un sistema inteligente que utiliza una arquitectura **RAG (Retrieval-Augmented Generation)** para recomendar ordenadores portátiles. El sistema utiliza una base de datos de grafos (**Neo4j**) para el almacenamiento técnico, **Ollama** para el procesamiento de lenguaje natural local (embeddings) y **Groq** como motor de razonamiento (LLM).

## 🚀 Instrucciones para el Despliegue (Docker)

Siga estos pasos para ejecutar la aplicación de forma totalmente automática.

### 1. Configuración de Variables de Entorno
Crea un archivo `.env` en la raíz y pega el contenido de abajo. Asegúrate de incluir tu Groq API Key donde se indica.

```env
# --- Configuración Neo4j ---
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j123
NEO4J_DATABASE=laptopdatabase

# --- Configuración LLM (Groq) ---
LLM_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=PONER_AQUI_TU_API_KEY_DE_GROQ

# --- Configuración Embeddings (Ollama) ---
EMBEDDING_MODEL=nomic-embed-text
```

## 2. Ejecución con Docker Compose
Abra una terminal en la carpeta raíz del proyecto y ejecute el comando de construcción y arranque:
```env
docker-compose up --build
```

Qué hará el sistema automáticamente?
Al ejecutar este comando, se activará un script de inicio (init-setup.sh) que realiza las siguientes tareas:

Ollama: Espera a que el servicio esté activo y descarga automáticamente el modelo de embeddings nomic-embed-text.

Neo4j: Levanta el servicio y configura la base de datos laptopdatabase.

Población de Datos: Ejecuta el script src/data/databaseGenerator.py para realizar el scraping de URLs reales y cargar los portátiles en el grafo.

App: Lanza la interfaz de usuario desarrollada en Streamlit.

## 3. Acceso y Pruebas
Una vez que la terminal indique que la aplicación está lista, abra su navegador en la dirección local proporcionada por Streamlit:
```env
http://localhost:8501
```

Ejemplos de consultas para probar:
Filtros Técnicos (Búsqueda Simbólica): "Busco un portátil con 16GB de RAM y una RTX 4060 por menos de 1300 euros".

Búsqueda Semántica: "Necesito un portátil muy ligero para viajar que tenga buena batería y sirva para oficina".