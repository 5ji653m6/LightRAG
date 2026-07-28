module.exports = {
  apps: [
    // Frontend: Vite/React via Bun
    {
      name: 'lightrag-webui-5173',
      cwd: './lightrag_webui',
      script: 'bun',
      args: 'run dev',
      env: { NODE_ENV: 'development' }
    },
    // Backend: FastAPI/uvicorn
    {
      name: 'lightrag-api-9621',
      cwd: '.',
      script: 'lightrag/api/start.cjs',
      interpreter: '/root/.nvm/versions/node/v24.13.0/bin/node',
      env: { PYTHONUNBUFFERED: '1' }
    }
  ]
}
