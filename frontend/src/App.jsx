function App() {
  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>CREDIT ASSISTANT</h1>
        <p style={styles.subtitle}>Environment setup successful.</p>
        <div style={styles.badge}>Phase 1 — Project Initialization</div>
        <div style={styles.stack}>
          <span style={styles.pill}>React + Vite</span>
          <span style={styles.pill}>FastAPI</span>
          <span style={styles.pill}>SQLAlchemy</span>
          <span style={styles.pill}>Google Gemini</span>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
    fontFamily: "'Segoe UI', system-ui, sans-serif",
  },
  card: {
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "16px",
    padding: "48px 56px",
    textAlign: "center",
    boxShadow: "0 25px 60px rgba(0,0,0,0.5)",
    maxWidth: "480px",
    width: "100%",
  },
  title: {
    color: "#f8fafc",
    fontSize: "2rem",
    fontWeight: "700",
    letterSpacing: "0.08em",
    margin: "0 0 12px",
  },
  subtitle: {
    color: "#94a3b8",
    fontSize: "1rem",
    margin: "0 0 28px",
  },
  badge: {
    display: "inline-block",
    background: "#0f172a",
    color: "#38bdf8",
    border: "1px solid #0ea5e9",
    borderRadius: "999px",
    padding: "6px 18px",
    fontSize: "0.8rem",
    fontWeight: "600",
    marginBottom: "28px",
    letterSpacing: "0.05em",
  },
  stack: {
    display: "flex",
    gap: "10px",
    flexWrap: "wrap",
    justifyContent: "center",
  },
  pill: {
    background: "#0f172a",
    color: "#64748b",
    border: "1px solid #334155",
    borderRadius: "6px",
    padding: "4px 14px",
    fontSize: "0.78rem",
    fontWeight: "500",
  },
};

export default App;
