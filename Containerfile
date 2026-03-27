FROM registry.access.redhat.com/ubi9/python-312:9.7@sha256:92c71d1e64cf84b9aa6e8e81555397175b9367298b456d24eac5b55ab41fdab9 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN python -m venv /tmp/venv \
    && /tmp/venv/bin/pip install --upgrade pip \
    && /tmp/venv/bin/pip install -r requirements.txt


FROM registry.access.redhat.com/ubi9/python-312-minimal:9.7@sha256:2ac60c655288a88ec55df5e2154b9654629491e3c58b5c54450fb3d27a575cb6

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONCOERCECLOCALE=0 \
    PYTHONUTF8=1 \
    PYTHONIOENCODING=UTF-8 \
    LANG=en_US.UTF-8
ENV PATH="/app-root/.venv/bin:$PATH"

WORKDIR /app-root/src

COPY --from=builder /tmp/venv /app-root/venv
COPY test_mcp_server.py .

EXPOSE 8888

CMD ["/app-root/venv/bin/python", "test_mcp_server.py"]
