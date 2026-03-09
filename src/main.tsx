import React from "react";
import ReactDOM from "react-dom/client";

function App() {
  return (
    <div style={{color:"white",fontFamily:"Arial",padding:"40px"}}>
      <h1>🚀 TrendPulse AI</h1>
      <p>Your AI trend prediction dashboard is live.</p>
      <a href="https://trend-pulse-ai.onrender.com">
        Open AI Engine
      </a>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
