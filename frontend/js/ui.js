/**
 * ui.js — Encapsulates UI rendering, highlighting, and logging
 */


class UI {
  static get CATEGORY_LABELS() {
    return {
      NAME: "Name", DATE: "Date", PHONE: "Phone",
      EMAIL: "Email", MRN: "MRN", SSN: "SSN",
      AADHAAR: "Aadhaar", ADDRESS: "Address",
    };
  }

  static highlightPseudonyms(text, tokenMap) {
    let html = this.escapeHtml(text);
    for (const p of Object.keys(tokenMap)) {
      html = html.split(this.escapeHtml(p)).join(`<span class="pseudo">${this.escapeHtml(p)}</span>`);
    }
    return html;
  }

  static highlightRestored(text, tokenMap) {
    let html = this.escapeHtml(text);
    for (const original of Object.values(tokenMap)) {
      html = html.split(this.escapeHtml(original)).join(`<span class="restored">${this.escapeHtml(original)}</span>`);
    }
    return html;
  }

  static renderTokenMap(tokenMap) {
    const tokenMapEl = document.getElementById("token-map");
    tokenMapEl.className = "flex flex-col gap-2.5";
    tokenMapEl.innerHTML = "";
    for (const [pseudonym, original] of Object.entries(tokenMap)) {
      const category = pseudonym.startsWith("Patient") ? "NAME" : pseudonym.split("_")[0];
      const row      = document.createElement("div");
      row.className  = "flex items-center justify-between p-3.5 bg-cream-50/50 border border-cream-200/50 rounded-xl font-mono text-[12px] group hover:bg-cream-50 transition-all duration-200";
      row.innerHTML  = `
        <span class="font-semibold text-teal-800">${this.escapeHtml(pseudonym)}</span>
        <span class="text-tertiary px-1"><i class="ti ti-arrow-right"></i></span>
        <span class="font-semibold text-purple-800 truncate max-w-[120px] sm:max-w-[200px]" title="${this.escapeHtml(original)}">${this.escapeHtml(original)}</span>
        <span class="text-[9px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded bg-cream-200 text-muted border border-cream-300/20 ml-auto mr-4">${this.CATEGORY_LABELS[category] || category}</span>
        <i class="ti ti-lock text-sm text-tertiary" title="Stored securely in Redis"></i>
      `;
      tokenMapEl.appendChild(row);
    }
  }

  static renderVaultTable(sessions, onDeleteSession) {
    const tbody = document.getElementById("vault-table-body");
    tbody.innerHTML = "";
    if (!sessions.length) {
      tbody.innerHTML = '<tr><td colspan="5" class="px-5 py-8 text-center text-xs text-tertiary bg-white border border-cream-200 rounded-b-xl shadow-sm">No sessions yet. Run a redaction to create one.</td></tr>';
      return;
    }
    for (const s of sessions) {
      const tr      = document.createElement("tr");
      tr.className  = "hover:bg-cream-50/50 transition-colors duration-150";
      tr.innerHTML  = `
        <td class="px-5 py-3.5 font-mono text-xs text-charcoal-800 border-b border-cream-100">${s.id}</td>
        <td class="px-5 py-3.5 text-xs text-muted border-b border-cream-100">${s.tokenCount}</td>
        <td class="px-5 py-3.5 text-xs text-muted border-b border-cream-100">${s.createdAt.toLocaleTimeString()}</td>
        <td class="px-5 py-3.5 text-xs text-muted border-b border-cream-100">${s.expiresInMins} min</td>
        <td class="px-5 py-3.5 text-right border-b border-cream-100">
          <button class="p-1.5 rounded-lg text-tertiary hover:text-coral-500 hover:bg-coral-50 focus:outline-none transition-all duration-200" data-session="${s.id}" title="Delete session from Redis">
            <i class="ti ti-trash text-base cursor-pointer"></i>
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    }
    tbody.querySelectorAll("[data-session]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.session;
        if (onDeleteSession) onDeleteSession(id);
      });
    });
  }

  static updateMetrics(sessions) {
    document.getElementById("metric-sessions").textContent = sessions.length;
    document.getElementById("metric-tokens").textContent   =
      sessions.reduce((s, sess) => s + sess.tokenCount, 0);
  }

  static logEvent(icon, message, auditEvents) {
    auditEvents.unshift({ icon, message, time: new Date() });
    const container  = document.getElementById("audit-log");
    container.innerHTML = "";
    for (const ev of auditEvents) {
      const div      = document.createElement("div");
      div.className  = "flex items-start gap-3 bg-white border border-cream-200 rounded-xl p-4 text-sm shadow-sm animate-fade-in";
      div.innerHTML  = `
        <div class="p-1.5 rounded bg-teal-50 text-teal-700 flex items-center justify-center"><i class="ti ${ev.icon} text-base"></i></div>
        <span class="text-xs font-medium text-charcoal-800 leading-relaxed mt-0.5">${this.escapeHtml(ev.message)}</span>
        <span class="ml-auto font-mono text-[10px] text-tertiary whitespace-nowrap mt-1">${ev.time.toLocaleTimeString()}</span>
      `;
      container.appendChild(div);
    }
  }

  static escapeHtml(str) {
    const d = document.createElement("div");
    d.textContent = str;
    return d.innerHTML;
  }
}

window.UI = UI;
