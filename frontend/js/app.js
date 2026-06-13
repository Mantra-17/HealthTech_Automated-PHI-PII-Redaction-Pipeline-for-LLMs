/**
 * app.js
 * ------
 * Wires up the dashboard: navigation between views, the redaction
 * flow (run redaction -> show token map -> simulate AI call ->
 * restore identities), the vault session table, and the audit log.
 */

// ---------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------
const navItems = document.querySelectorAll(".nav-item");
const views = document.querySelectorAll(".view");

navItems.forEach((item) => {
  item.addEventListener("click", (e) => {
    e.preventDefault();
    const target = item.dataset.view;

    navItems.forEach((i) => i.classList.remove("active"));
    views.forEach((v) => v.classList.remove("active"));

    item.classList.add("active");
    document.getElementById(`view-${target}`).classList.add("active");
  });
});

// ---------------------------------------------------------------
// State
// ---------------------------------------------------------------
const sessions = []; // { id, tokenMap, createdAt }
const auditEvents = [];

const CATEGORY_LABELS = {
  NAME: "Name",
  DATE: "Date",
  PHONE: "Phone",
  EMAIL: "Email",
  MRN: "MRN",
  SSN: "SSN",
  AADHAAR: "Aadhaar",
  ADDRESS: "Address",
};

// ---------------------------------------------------------------
// Elements
// ---------------------------------------------------------------
const inputNote = document.getElementById("input-note");
const outputRedacted = document.getElementById("output-redacted");
const outputFinal = document.getElementById("output-final");
const tokenMapEl = document.getElementById("token-map");
const btnRedact = document.getElementById("btn-redact");
const btnSendAI = document.getElementById("btn-send-ai");
const btnClear = document.getElementById("btn-clear");

let currentSession = null;

// ---------------------------------------------------------------
// Run redaction
// ---------------------------------------------------------------
btnRedact.addEventListener("click", () => {
  const text = inputNote.value.trim();
  if (!text) return;

  const { cleanText, tokenMap, entities } = redact(text);

  if (Object.keys(tokenMap).length === 0) {
    outputRedacted.classList.add("placeholder");
    outputRedacted.classList.remove("output-box");
    outputRedacted.textContent = "No PHI detected in this note.";
    return;
  }

  // Render redacted text with highlighted pseudonyms
  outputRedacted.classList.remove("placeholder");
  outputRedacted.innerHTML = highlightPseudonyms(cleanText, tokenMap);

  // Render token map
  renderTokenMap(tokenMap);

  // Reset AI output
  outputFinal.classList.add("placeholder");
  outputFinal.textContent = "The AI's response, with patient identity restored, will appear here.";

  // Create / update session
  currentSession = {
    id: newSessionId(),
    tokenMap,
    cleanText,
    createdAt: new Date(),
  };
  sessions.unshift(currentSession);
  renderVaultTable();
  updateMetrics();

  logEvent("ti-scan", `Redacted note — ${Object.keys(tokenMap).length} entities detected, session ${currentSession.id} created.`);

  btnSendAI.disabled = false;
});

// ---------------------------------------------------------------
// Clear
// ---------------------------------------------------------------
btnClear.addEventListener("click", () => {
  inputNote.value = "";
  outputRedacted.className = "output-box placeholder";
  outputRedacted.textContent = "Run redaction to see the de-identified version of this note.";
  outputFinal.className = "output-box placeholder";
  outputFinal.textContent = "The AI's response, with patient identity restored, will appear here.";
  tokenMapEl.className = "token-map placeholder";
  tokenMapEl.textContent = "No active session. Token mappings will appear here after redaction.";
  btnSendAI.disabled = true;
  currentSession = null;
});

// ---------------------------------------------------------------
// Send to AI (simulated)
// ---------------------------------------------------------------
btnSendAI.addEventListener("click", () => {
  if (!currentSession) return;

  btnSendAI.disabled = true;
  btnSendAI.innerHTML = '<i class="ti ti-loader-2"></i> Waiting for AI response...';

  logEvent("ti-cloud-upload", `Sent pseudonymized text to external AI (session ${currentSession.id}).`);

  setTimeout(() => {
    const pseudoResponse = buildMockAIResponse(currentSession.tokenMap);
    const restored = restore(pseudoResponse, currentSession.tokenMap);

    outputFinal.classList.remove("placeholder");
    outputFinal.innerHTML = highlightRestored(restored, currentSession.tokenMap);

    logEvent("ti-replace", `AI response received and identities restored (session ${currentSession.id}).`);

    btnSendAI.innerHTML = '<i class="ti ti-sparkles"></i> Send to AI assistant';
    btnSendAI.disabled = false;
  }, 1100);
});

// ---------------------------------------------------------------
// Helpers — rendering
// ---------------------------------------------------------------
function highlightPseudonyms(text, tokenMap) {
  let html = escapeHtml(text);
  for (const pseudonym of Object.keys(tokenMap)) {
    const re = new RegExp(escapeRegex(pseudonym), "g");
    html = html.replace(re, `<span class="pseudo">${escapeHtml(pseudonym)}</span>`);
  }
  return html;
}

function highlightRestored(text, tokenMap) {
  let html = escapeHtml(text);
  for (const original of Object.values(tokenMap)) {
    const re = new RegExp(escapeRegex(escapeHtml(original)), "g");
    html = html.replace(re, `<span class="restored">${escapeHtml(original)}</span>`);
  }
  return html;
}

function renderTokenMap(tokenMap) {
  tokenMapEl.classList.remove("placeholder");
  tokenMapEl.innerHTML = "";

  for (const [pseudonym, original] of Object.entries(tokenMap)) {
    const category = pseudonym.startsWith("Patient") ? "NAME" : pseudonym.split("_")[0];
    const row = document.createElement("div");
    row.className = "token-row";
    row.innerHTML = `
      <span class="pseudo-label">${escapeHtml(pseudonym)}</span>
      <span class="arrow"><i class="ti ti-arrow-right"></i></span>
      <span class="original-label">${escapeHtml(original)}</span>
      <span class="category-badge">${CATEGORY_LABELS[category] || category}</span>
      <i class="ti ti-lock" title="Stored in Redis vault"></i>
    `;
    tokenMapEl.appendChild(row);
  }
}

function renderVaultTable() {
  const tbody = document.getElementById("vault-table-body");
  tbody.innerHTML = "";

  if (sessions.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty-row">No sessions yet. Run a redaction to create one.</td></tr>';
    return;
  }

  for (const session of sessions) {
    const tr = document.createElement("tr");
    const ttlMinutes = 30;
    tr.innerHTML = `
      <td>${session.id}</td>
      <td>${Object.keys(session.tokenMap).length}</td>
      <td>${session.createdAt.toLocaleTimeString()}</td>
      <td>${ttlMinutes} min</td>
      <td><i class="ti ti-trash" style="cursor:pointer; color: var(--text-tertiary);" data-session="${session.id}"></i></td>
    `;
    tbody.appendChild(tr);
  }

  // Wire up delete buttons
  tbody.querySelectorAll("[data-session]").forEach((icon) => {
    icon.addEventListener("click", () => {
      const id = icon.dataset.session;
      const idx = sessions.findIndex((s) => s.id === id);
      if (idx !== -1) {
        sessions.splice(idx, 1);
        logEvent("ti-trash", `Vault session ${id} deleted.`);
        renderVaultTable();
        updateMetrics();
      }
    });
  });
}

function updateMetrics() {
  document.getElementById("metric-sessions").textContent = sessions.length;
  const totalTokens = sessions.reduce((sum, s) => sum + Object.keys(s.tokenMap).length, 0);
  document.getElementById("metric-tokens").textContent = totalTokens;
}

function logEvent(icon, message) {
  auditEvents.unshift({ icon, message, time: new Date() });
  renderAuditLog();
}

function renderAuditLog() {
  const container = document.getElementById("audit-log");
  if (auditEvents.length === 0) {
    container.innerHTML = '<p class="empty-row">No events yet.</p>';
    return;
  }
  container.innerHTML = "";
  for (const event of auditEvents) {
    const div = document.createElement("div");
    div.className = "audit-entry";
    div.innerHTML = `
      <i class="ti ${event.icon}"></i>
      <span>${escapeHtml(event.message)}</span>
      <span class="audit-time">${event.time.toLocaleTimeString()}</span>
    `;
    container.appendChild(div);
  }
}

// ---------------------------------------------------------------
// Mock AI response generator
// ---------------------------------------------------------------
function buildMockAIResponse(tokenMap) {
  const patientLabel = Object.keys(tokenMap).find((k) => k.startsWith("Patient")) || "Patient A";
  return `Summary: ${patientLabel} presents with respiratory symptoms consistent with a mild lower respiratory tract infection. Recommend completing the prescribed antibiotic course, repeat chest imaging if symptoms persist beyond 5 days, and a follow-up consult to review results. No red-flag findings noted for ${patientLabel} at this time.`;
}

// ---------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
