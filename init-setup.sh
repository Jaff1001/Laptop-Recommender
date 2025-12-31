#!/bin/bash
echo "Esperando a que el servicio Ollama arranque..."
while ! curl -s http://ollama:11434/api/tags > /dev/null; do
  sleep 3
done

echo "Descargando modelo de embeddings..."
curl -X POST http://ollama:11434/api/pull -d "{\"name\": \"${EMBEDDING_MODEL:-nomic-embed-text}\"}"

echo "Esperando a que Neo4j responda en el puerto 7687..."
while ! nc -z neo4j 7687; do   
  sleep 3
done

FLAG_FILE="/app/.db_initialized"

if [ -f "$FLAG_FILE" ]; then
  echo "La base de datos ya ha sido inicializada anteriormente (flag encontrado). Saltando..."
else
  echo "Poblando la base de datos laptopdatabase..."
  if python src/data/databaseGenerator.py; then
    touch "$FLAG_FILE"
    echo "Población completada y marca de control creada."
  else
    echo "Error al poblar la base de datos."
  fi
fi

echo "Iniciando la aplicación..."
python run_app.py