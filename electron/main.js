const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');
const os = require('os');

let flaskProcess = null;
let mainWindow = null;

// Helper: poll Flask until it responds
async function waitForFlaskReady(maxAttempts = 60, delayMs = 500) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const response = await new Promise((resolve, reject) => {
        http.get('http://localhost:5000/', (res) => {
          resolve(res.statusCode === 200);
        }).on('error', reject);
      });
      if (response) {
        console.log('[Electron] Flask is ready');
        return true;
      }
    } catch (e) {
      // Flask not ready yet
      console.log(`[Electron] Waiting for Flask... (attempt ${i + 1}/${maxAttempts})`);
    }
    await new Promise(r => setTimeout(r, delayMs));
  }
  return false;
}

// Spawn Flask subprocess
function startFlask() {
  console.log('[Electron] Starting Flask subprocess...');
  
  // Determine Python path: use bundled Python if available, otherwise system Python
  const bundledPythonPath = path.join(__dirname, 'resources', 'python-bundle', 'python.exe');
  const pythonPath = require('fs').existsSync(bundledPythonPath) ? bundledPythonPath : 'python';
  
  const appPyPath = path.join(__dirname, '..', 'src', 'app_flask.py');
  
  flaskProcess = spawn(pythonPath, [appPyPath], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: path.join(__dirname, '..'),
  });
  
  flaskProcess.stdout.on('data', (data) => {
    console.log(`[Flask] ${data.toString().trim()}`);
  });
  
  flaskProcess.stderr.on('data', (data) => {
    console.log(`[Flask stderr] ${data.toString().trim()}`);
  });
  
  flaskProcess.on('error', (err) => {
    console.error('[Electron] Failed to start Flask:', err);
  });
  
  flaskProcess.on('exit', (code, signal) => {
    console.log(`[Electron] Flask exited with code ${code}, signal ${signal}`);
    flaskProcess = null;
  });
  
  return flaskProcess;
}

// Create main window
async function createWindow() {
  console.log('[Electron] Creating main window...');
  
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });
  
  // Wait for Flask to be ready before loading
  const flaskReady = await waitForFlaskReady();
  if (!flaskReady) {
    console.error('[Electron] Flask failed to start. Exiting.');
    app.quit();
    return;
  }
  
  mainWindow.loadURL('http://localhost:5000');
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// App lifecycle
app.on('ready', async () => {
  console.log('[Electron] App ready, starting Flask...');
  startFlask();
  
  // Give Flask a moment to start before creating window
  setTimeout(createWindow, 1000);
});

app.on('window-all-closed', () => {
  console.log('[Electron] All windows closed, quitting app...');
  if (flaskProcess) {
    console.log('[Electron] Terminating Flask subprocess...');
    flaskProcess.kill();
  }
  app.quit();
});

app.on('quit', () => {
  if (flaskProcess && !flaskProcess.killed) {
    console.log('[Electron] Forcefully terminating Flask...');
    flaskProcess.kill('SIGKILL');
  }
});

// Catch unhandled exceptions
process.on('uncaughtException', (err) => {
  console.error('[Electron] Uncaught exception:', err);
  if (flaskProcess) flaskProcess.kill();
  app.quit();
});
