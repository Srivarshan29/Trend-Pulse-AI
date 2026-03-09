import express from "express";
import { createServer as createViteServer } from "vite";
import { WebSocketServer, WebSocket } from "ws";
import http from "http";

async function startServer() {
  const app = express();
  const server = http.createServer(app);
  const PORT = 3000;

  // WebSocket server
  const wss = new WebSocketServer({ server });

  wss.on("connection", (ws) => {
    console.log("Client connected");
    let analysisInterval: NodeJS.Timeout | null = null;

    ws.on("message", (message) => {
      try {
        const data = JSON.parse(message.toString());
        
        if (data.type === "START_ANALYSIS") {
          const { topic } = data;
          console.log(`Starting analysis for: ${topic}`);
          
          if (analysisInterval) {
            clearInterval(analysisInterval);
          }

          // Send initial status
          ws.send(JSON.stringify({
            type: "ANALYSIS_UPDATE",
            status: "Initializing data collection...",
            progress: 10,
            result: null
          }));

          let progress = 10;
          
          // Simulate real-time progress updates
          analysisInterval = setInterval(() => {
            progress += Math.floor(Math.random() * 15) + 5;
            
            if (progress >= 100) {
              clearInterval(analysisInterval!);
              
              // Final result
              const probability = Math.random() * 0.5 + 0.4;
              ws.send(JSON.stringify({
                type: "ANALYSIS_COMPLETE",
                status: "Analysis complete",
                progress: 100,
                result: {
                  topic,
                  probability,
                  growth: probability > 0.75 ? 'High 🔥' : probability > 0.5 ? 'Medium 📈' : 'Low 📉',
                  sentiment: `+${(Math.random() * 0.5 + 0.3).toFixed(2)} (Positive)`
                }
              }));
            } else {
              // Intermediate updates
              const statuses = [
                "Scraping social media data...",
                "Analyzing sentiment with NLP...",
                "Running time-series forecasting...",
                "Calculating virality score...",
                "Finalizing report..."
              ];
              const statusIndex = Math.min(Math.floor((progress / 100) * statuses.length), statuses.length - 1);
              
              ws.send(JSON.stringify({
                type: "ANALYSIS_UPDATE",
                status: statuses[statusIndex],
                progress,
                result: null
              }));
            }
          }, 1500); // Send update every 1.5 seconds
        }
      } catch (error) {
        console.error("Error parsing message:", error);
      }
    });

    ws.on("close", () => {
      console.log("Client disconnected");
      if (analysisInterval) {
        clearInterval(analysisInterval);
      }
    });
  });

  // API routes
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok" });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static("dist"));
  }

  server.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
