/**
 * view-logs.js — Custom Web Component for Audit Log View
 */

class ViewLogs extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <header class="mb-6 md:mb-8 pb-4 border-b border-cream-200">
        <h1>Audit log</h1>
        <p class="text-sm text-muted mt-1">Every redaction and restoration event, for compliance review</p>
      </header>

      <div id="audit-log" class="max-w-3xl flex flex-col gap-3">
        <p class="px-5 py-8 text-center text-xs text-tertiary bg-white border border-cream-200 rounded-xl shadow-sm">No events yet.</p>
      </div>
    `;
  }
}

customElements.define("view-logs", ViewLogs);
