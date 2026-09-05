import express from "express";
import { spawn, ChildProcess } from "child_process";
import { createProxyMiddleware } from "http-proxy-middleware";

const app = express();
const PORT = 3000;
const PYTHON_PORT = 8000;

let pythonProcess: ChildProcess | null = null;

function startPythonBackend() {
  console.log("[Node Server] Spawning Python FastAPI backend on port " + PYTHON_PORT + "...");
  pythonProcess = spawn("python3", [
    "-m",
    "uvicorn",
    "app.main:app",
    "--host",
    "127.0.0.1",
    "--port",
    String(PYTHON_PORT),
  ], {
    stdio: "inherit",
    env: { ...process.env, PORT: String(PYTHON_PORT) }
  });

  pythonProcess.on("error", (err) => {
    console.error("[Node Server] Failed to spawn Python process:", err);
  });

  pythonProcess.on("exit", (code, signal) => {
    console.log(`[Node Server] Python process exited with code ${code}, signal ${signal}`);
  });
}

// Clean termination handling
function cleanup() {
  if (pythonProcess) {
    console.log("[Node Server] Terminating Python process...");
    pythonProcess.kill("SIGTERM");
    pythonProcess = null;
  }
}

process.on("SIGINT", () => {
  cleanup();
  process.exit(0);
});

process.on("SIGTERM", () => {
  cleanup();
  process.exit(0);
});

process.on("exit", cleanup);

// Forward all traffic to the Python FastAPI backend
app.use(
  "/",
  createProxyMiddleware({
    target: `http://127.0.0.1:${PYTHON_PORT}`,
    changeOrigin: true,
    ws: true,
    on: {
      error: (err, req, res: any) => {
        console.warn("[Node Proxy] Waiting for Python backend to be ready...", err.message);
        if (res && typeof res.status === "function" && !res.headersSent) {
          res.status(503).send(`
            <!DOCTYPE html>
            <html>
              <head>
                <meta http-equiv="refresh" content="2">
                <title>Starting AI News Hub...</title>
                <style>
                  body { font-family: -apple-system, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; background: #0f172a; color: #f8fafc; margin: 0; }
                  .box { text-align: center; }
                  .spinner { font-size: 32px; animation: spin 1s infinite linear; display: inline-block; }
                  @keyframes spin { 100% { transform: rotate(360deg); } }
                </style>
              </head>
              <body>
                <div class="box">
                  <div class="spinner">⚙️</div>
                  <h2>Starting AI News Hub Engine...</h2>
                  <p>Initializing SQLite database and RSS collector services.</p>
                </div>
              </body>
            </html>
          `);
        }
      },
    },
  })
);

startPythonBackend();

app.listen(PORT, "0.0.0.0", () => {
  console.log(`[Node Server] Reverse proxy listening on http://0.0.0.0:${PORT} -> http://127.0.0.1:${PYTHON_PORT}`);
});
