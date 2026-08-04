#!/bin/bash
cd /data/workspace/lightrag_all/LightRAG
/data/workspace/lightrag_all/LightRAG/.venv/bin/lightrag-server --host 0.0.0.0 --port 9621 --working-dir /data/workspace/lightrag_all/LightRAG/data/rag_storage_9621
