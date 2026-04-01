import express from "express";
import cors from "cors";
import { HappyRobotClient, ApiError } from "@happyrobot-ai/sdk";

const PORT = process.env.PORT ?? 3001;
const API_KEY = process.env.HAPPYROBOT_API_KEY;
const WORKFLOW_ID = process.env.WORKFLOW_ID;

/** Must match where the workflow is published in HappyRobot: development | staging | production */
const _envRaw = (
  process.env.HAPPYROBOT_ENVIRONMENT ||
  process.env.WORKFLOW_ENVIRONMENT ||
  "development"
).toLowerCase();
const WORKFLOW_ENV = (["development", "staging", "production"].includes(_envRaw)
  ? _envRaw
  : "development") as "development" | "staging" | "production";

if (!API_KEY) {
  console.error("Missing HAPPYROBOT_API_KEY environment variable");
  process.exit(1);
}

if (!WORKFLOW_ID) {
  console.error("Missing WORKFLOW_ID environment variable");
  process.exit(1);
}

const client = new HappyRobotClient({ apiKey: API_KEY });

const app = express();
// Allow any localhost / 127.0.0.1 port (Vite often uses 5174+ when 5173 is busy)
app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin) return callback(null, true);
      try {
        const u = new URL(origin);
        const ok =
          (u.hostname === "localhost" || u.hostname === "127.0.0.1") &&
          (u.protocol === "http:" || u.protocol === "https:");
        callback(null, ok);
      } catch {
        callback(null, false);
      }
    },
    credentials: true,
  })
);
app.use(express.json());

app.post("/api/voice/token", async (_req, res) => {
  try {
    const result = await client.voice.createToken({
      workflow_id: WORKFLOW_ID,
      env: WORKFLOW_ENV,
    });
    res.json(result);
  } catch (err) {
    console.error("Failed to create voice token:", err);
    if (err instanceof ApiError) {
      const msg =
        err.body?.message ||
        err.body?.error ||
        err.message ||
        `HappyRobot API error (${err.status})`;
      return res.status(err.status >= 400 && err.status < 600 ? err.status : 500).json({
        error: "Failed to create voice token",
        detail: msg,
        status: err.status,
        hint:
          err.status === 401
            ? "Check HAPPYROBOT_API_KEY in server/.env"
            : err.status === 404
              ? "Check WORKFLOW_ID and HAPPYROBOT_ENVIRONMENT (dev vs production publish)"
              : undefined,
      });
    }
    const message = err instanceof Error ? err.message : String(err);
    res.status(500).json({
      error: "Failed to create voice token",
      detail: message,
      hint: `Using environment="${WORKFLOW_ENV}". If the workflow is only published to Production, set HAPPYROBOT_ENVIRONMENT=production in server/.env`,
    });
  }
});

app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
  console.log(`HappyRobot voice: workflow=${WORKFLOW_ID} environment=${WORKFLOW_ENV}`);
});
