FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements-ml.txt ./

# CPU-only PyTorch first, so sentence-transformers does not pull the multi-gigabyte CUDA build.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt -r requirements-ml.txt

# Bake the embedding model into the image so the service starts without downloading anything.
ARG PRELOAD_MODEL=true
ARG EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
ENV HF_HOME=/models
RUN if [ "$PRELOAD_MODEL" = "true" ]; then \
        python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${EMBEDDING_MODEL_NAME}')"; \
    fi

COPY . .

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
