module.exports = {
  apps: [
    {
      name: 'lightrag-9622',
      cwd: '/data/workspace/lightrag_all/LightRAG',
      script: './start-9622.sh',
      interpreter: 'bash',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    }
  ]
}
