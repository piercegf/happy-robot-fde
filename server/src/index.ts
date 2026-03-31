import express from "express";
import cors from "cors";
import { HappyRobotClient } from "@happyrobot-ai/sdk";

const PORT = process.env.PORT ?? 3001;
const API_KEY = process.env.HAPPYROBOT_API_KEY;
const WORKFLOW_ID = process.env.WORKFLOW_ID;

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
app.use(cors({ origin: "http://localhost:5173" }));
app.use(express.json());

app.post("/api/voice/token", async (_req, res) => {
  try {
    const result = await client.voice.createToken({
      workflow_id: WORKFLOW_ID,
      environment: "development",
    });
    res.json(result);
  } catch (err) {
    console.error("Failed to create voice token:", err);
    res.status(500).json({ error: "Failed to create voice token" });
  }
});

app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
