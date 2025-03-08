FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml ./pyproject.toml

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    export PATH="/root/.cargo/bin:$PATH" && \
    uv pip install --system -e .

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
