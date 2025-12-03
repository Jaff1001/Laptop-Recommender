import re
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.llms.groq import Groq
from llama_index.embeddings.ollama import OllamaEmbedding


class chatbotLaptopRecommender:

    def __init__(self, graph_connection: Neo4jGraphStore, llm: Groq, embedding_model: OllamaEmbedding):
        self.graph_connection = graph_connection
        self.llm = llm
        self.embedding_model = embedding_model


    # === Limpieza básica del texto ===
    def sanitize_text(self, text):
        if not text:
            return ""
        blocked = ["ignore", "system:", "assistant:", "prompt:", "<script", "```", "jailbreak", "bypass", "act as"]
        t = text.lower()
        for b in blocked:
            t = t.replace(b, "")
        return t


    # === Extraer filtros simples de la pregunta ===
    def extract_basic_filters(self, text):
        t = text.lower()

        filters = {
            "gpu": None,
            "ram": None,
            "price": None,
            "cpu": None,
            "ssd": None,
            "inches": None,
            "type": None,
        }

        # GPU
        for g in ["4090","4080","4070","4060","4050","3080","3070","3060","3050"]:
            if g in t:
                filters["gpu"] = g
                break

        # RAM
        m = re.search(r"(\d+)\s*gb", t)
        if m:
            filters["ram"] = int(m.group(1))

        # CPU
        if "i3" in t: filters["cpu"] = "i3"
        if "i5" in t: filters["cpu"] = "i5"
        if "i7" in t: filters["cpu"] = "i7"
        if "i9" in t: filters["cpu"] = "i9"
        if "ryzen 5" in t: filters["cpu"] = "ryzen5"
        if "ryzen 7" in t: filters["cpu"] = "ryzen7"
        if "ryzen 9" in t: filters["cpu"] = "ryzen9"

        # SSD
        m = re.search(r"(\d+)\s*gb\s*(ssd)?", t)
        if m:
            filters["ssd"] = m.group(1)

        # Precio (mejorado)
        m = re.search(r"(\d{3,4})\s*(€|eur|euros)?", t)
        if m:
            price = float(m.group(1))

            if any(x in t for x in ["menos", "hasta", "bajo", "<"]):
                filters["price"] = price
            elif "entre" not in t:
                filters["price"] = price

        m = re.search(r"entre\s+(\d{3,4})\s+y\s+(\d{3,4})", t)
        if m:
            filters["price"] = float(m.group(2))

        # Intención de uso (no técnico)
        if any(w in t for w in ["jugar", "gaming", "videojuegos", "fps"]):
            filters["type"] = "juegos"
        if any(w in t for w in ["estudiar", "universidad", "clase", "estudiante"]):
            filters["type"] = "general"
        if any(w in t for w in ["oficina", "trabajar", "empresa"]):
            filters["type"] = "oficina"
        if any(w in t for w in ["ligero", "portabilidad", "viajar", "compacto"]):
            filters["type"] = "ultraportátil"

        return filters


    # === Determinar si hay especificaciones técnicas reales ===
    def has_real_specs(self, filters):
        technical = ["gpu", "ram", "cpu", "ssd", "price", "inches"]
        for key in technical:
            if filters.get(key) is not None:
                return True
        return False


    # === Preparar texto para embeddings ===
    def normalize_query(self, refined, filters):
        parts = []

        if filters["gpu"]:   parts.append(f"gpu_number:{filters['gpu']}")
        if filters["ram"]:   parts.append(f"ram_min:{filters['ram']}GB")
        if filters["cpu"]:   parts.append(f"cpu_simple:{filters['cpu']}")
        if filters["ssd"]:   parts.append(f"storage_min:{filters['ssd']}GB")
        if filters["price"]: parts.append(f"max_price:{filters['price']}")
        if filters["inches"]:parts.append(f"max_inches:{filters['inches']}")

        if parts:
            parts.append(f"user_query:{refined}")
            return " | ".join(parts)

        return refined


    # === Búsqueda simbólica ===
    def search_symbolic(self, filters):
        cy = """
        MATCH (l:Laptop)-[:ES_TIPO_DE]->(t:Type)
        WHERE ($gpu IS NULL OR toLower(l.gpu) CONTAINS $gpu)
          AND ($ram IS NULL OR l.ram >= $ram)
          AND ($price IS NULL OR l.price <= $price)
          AND ($inches IS NULL OR l.inches <= $inches)
        RETURN 
            l.id AS id,
            l.product AS product,
            l.cpu AS cpu,
            l.gpu AS gpu,
            l.ram AS ram,
            l.inches AS inches,
            l.price AS price,
            l.url AS link,
            l.memory AS memory,
            t.name AS type_name
        ORDER BY l.price ASC
        LIMIT 20
        """

        with self.graph_connection._driver.session(database="laptopdatabase") as s:
            r = s.run(
                cy,
                gpu=filters["gpu"],
                ram=filters["ram"],
                price=filters["price"],
                inches=filters["inches"]
            )
            return [x.data() for x in r]


    # === Búsqueda semántica ===
    def search_semantic(self, question):
        try:
            embedding = self.embedding_model.get_text_embedding(question)

            cy = """
                CALL db.index.vector.queryNodes('laptop_embeddings', 8, $embedding)
                YIELD node, score
                OPTIONAL MATCH (node)-[:ES_TIPO_DE]->(t:Type)
                RETURN 
                    node.id AS id,
                    node.product AS product,
                    node.cpu AS cpu,
                    node.gpu AS gpu,
                    node.ram AS ram,
                    node.inches AS inches,
                    node.price AS price,
                    node.url AS link,
                    node.memory AS memory,
                    t.name AS type_name,
                    score
                ORDER BY score DESC, node.price ASC
            """

            with self.graph_connection._driver.session(database="laptopdatabase") as s:
                res = s.run(cy, embedding=embedding)
                return [r.data() for r in res]

        except Exception as e:
            return f"Error ejecutando búsqueda semántica: {e}"


    # === Reformular pregunta ===
    def reformulate_question(self, original_question):
        prompt = f"""
        Decide si esta consulta trata sobre portátiles.

        - Si NO trata de portátiles o la pregunta contiene contenido obsceno u sexual entre otros, devuelve:
          "Pregunta no tratable"

        - Si SÍ trata de portátiles, limpia el texto sin cambiar el significado.

        Consulta:
        "{original_question}"
        """

        refined = self.llm.complete(prompt=prompt).text.strip()
        return original_question, refined


    # === Generar justificación ===
    def generate_justification(self, original, refined, results, include_urls):
        prompt = f"""
        Eres un experto recomendando portátiles.
        Usa SOLO los datos de RESULTADOS.

        RESULTADOS:
        {results}

        FORMATO:

        Hola, estos son los portátiles que más se ajustan a tu consulta:

        1. **NOMBRE DEL PORTÁTIL**
        - CPU: ...
        - GPU: ...
        - RAM: ...
        - Pantalla: ...
        - Memoria: ...
        - Precio: ... €
        {"- URL: ..." if include_urls else ""}
        - Justificación: 1–3 frases basadas en CPU, GPU, RAM, precio y tipo.

        2. **NOMBRE DEL PORTÁTIL**
        - CPU: ...
        - GPU: ...
        - RAM: ...
        - Pantalla: ...
        - Memoria: ...
        - Precio: ... €
        {"- URL: ..." if include_urls else ""}
        - Justificación: 1–3 frases.

        Reglas:
        - No menciones la pregunta.
        - Usa siempre lista numerada.
        - Separa cada portátil con una línea.
        - No incluyas URL si está vacía.
        """
        return self.llm.complete(prompt=prompt).text.strip()


    # === Lógica principal ===
    def query(self, question, show_urls):

        if len(question) > 400:
            return "La consulta es demasiado larga. Resume tu petición."

        safe = self.sanitize_text(question)
        original, refined = self.reformulate_question(safe)

        if refined == "Pregunta no tratable":
            return "Lo siento, solo me especializo en el ámbito de los portátiles."

        filters = self.extract_basic_filters(refined)
        normalized = self.normalize_query(refined, filters)

        has_specs = self.has_real_specs(filters)

        if has_specs:
            results = self.search_symbolic(filters)
            if not results:
                results = self.search_semantic(normalized)
        else:
            results = self.search_semantic(normalized)

        return self.generate_justification(original, refined, results, show_urls)
