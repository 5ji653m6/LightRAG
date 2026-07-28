const { spawn } = require('child_process');
const path = require('path');

const proc = spawn('python3', ['-m', 'uvicorn', 'lightrag.api.lightrag_server:app', '--host', '0.0.0.0', '--port', '9621', '--reload'], {
  cwd: path.resolve(__dirname, '../..'),
  stdio: 'inherit',
  windowsHide: true,
  env: { ...process.env, PYTHONUNBUFFERED: '1' }
});

proc.on('close', (code) => process.exit(code));
proc.on('error', (err) => {
  console.error('Failed to start backend:', err.message);
  process.exit(1);
});
