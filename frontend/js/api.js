/**
 * api.js — Encapsulates backend HTTP fetch calls
 */

class API {
  static get BASE_URL() {
    // Dynamically detect if running locally or in the cloud
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
      return "http://localhost:5001/api";
    }
    return `${window.location.origin}/api`;
  }

  static async redact(text) {
    const response = await fetch(`${this.BASE_URL}/redact`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || "Backend redaction failed");
    }
    return response.json();
  }

  static async ask(sessionId, cleanText) {
    const response = await fetch(`${this.BASE_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        clean_text: cleanText
      })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || "Backend AI call failed");
    }
    return response.json();
  }

  static async getSessions() {
    const response = await fetch(`${this.BASE_URL}/sessions`);
    if (!response.ok) {
      throw new Error("Failed to fetch backend sessions");
    }
    return response.json();
  }

  static async deleteSession(sessionId) {
    const response = await fetch(`${this.BASE_URL}/sessions/${sessionId}`, {
      method: "DELETE"
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || "Failed to delete session from database");
    }
    return response.json();
  }

  static async evaluate(groundTruth, predictions, mode = "exact", strictType = true, aggregation = "micro") {
    const response = await fetch(`${this.BASE_URL}/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ground_truth: groundTruth,
        predictions: predictions,
        mode: mode,
        strict_type: strictType,
        aggregation: aggregation
      })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || "Evaluation request failed");
    }
    return response.json();
  }

  static async getEvaluationSampleNotes() {
    const response = await fetch(`${this.BASE_URL}/evaluate/sample-notes`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || "Failed to fetch evaluation sample notes");
    }
    return response.json();
  }
}

window.API = API;
