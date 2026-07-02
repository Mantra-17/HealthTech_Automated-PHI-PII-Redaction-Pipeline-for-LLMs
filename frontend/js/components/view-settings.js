/**
 * view-settings.js — Custom Web Component for Settings View
 */

class ViewSettings extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <header class="mb-6 md:mb-8 pb-4 border-b border-cream-200">
        <h1>Settings</h1>
        <p class="text-sm text-muted mt-1">Configure detection rules and proxy behaviour</p>
      </header>

      <!-- Card: Detection Categories -->
      <div class="max-w-2xl bg-white border border-cream-200 rounded-xl p-5 md:p-6 shadow-sm flex flex-col gap-4 mb-6 animate-fade-in">
        <h3 class="text-sm font-semibold text-charcoal-800 border-b border-cream-100 pb-3">Detection categories</h3>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <label class="flex items-center gap-2.5 text-xs font-medium text-muted bg-cream-50 border border-cream-200 p-2.5 rounded-lg opacity-85 cursor-not-allowed">
            <input type="checkbox" checked disabled class="accent-teal-600 w-3.5 h-3.5" />
            <span>Names</span>
          </label>
          <label class="flex items-center gap-2.5 text-xs font-medium text-muted bg-cream-50 border border-cream-200 p-2.5 rounded-lg opacity-85 cursor-not-allowed">
            <input type="checkbox" checked disabled class="accent-teal-600 w-3.5 h-3.5" />
            <span>Dates</span>
          </label>
          <label class="flex items-center gap-2.5 text-xs font-medium text-muted bg-cream-50 border border-cream-200 p-2.5 rounded-lg opacity-85 cursor-not-allowed">
            <input type="checkbox" checked disabled class="accent-teal-600 w-3.5 h-3.5" />
            <span>Phone numbers</span>
          </label>
          <label class="flex items-center gap-2.5 text-xs font-medium text-muted bg-cream-50 border border-cream-200 p-2.5 rounded-lg opacity-85 cursor-not-allowed">
            <input type="checkbox" checked disabled class="accent-teal-600 w-3.5 h-3.5" />
            <span>Emails</span>
          </label>
          <label class="flex items-center gap-2.5 text-xs font-medium text-muted bg-cream-50 border border-cream-200 p-2.5 rounded-lg opacity-85 cursor-not-allowed">
            <input type="checkbox" checked disabled class="accent-teal-600 w-3.5 h-3.5" />
            <span>MRN / patient IDs</span>
          </label>
          <label class="flex items-center gap-2.5 text-xs font-medium text-muted bg-cream-50 border border-cream-200 p-2.5 rounded-lg opacity-85 cursor-not-allowed">
            <input type="checkbox" checked disabled class="accent-teal-600 w-3.5 h-3.5" />
            <span>Addresses</span>
          </label>
          <label class="flex items-center gap-2.5 text-xs font-medium text-muted bg-cream-50 border border-cream-200 p-2.5 rounded-lg opacity-85 cursor-not-allowed">
            <input type="checkbox" checked disabled class="accent-teal-600 w-3.5 h-3.5" />
            <span>Aadhaar / SSN</span>
          </label>
        </div>
        <p class="text-[11px] text-tertiary leading-relaxed mt-2">These map directly to the regex + NLP rules implemented in <code class="font-mono bg-cream-100 text-charcoal-800 px-1.5 py-0.5 rounded text-[10px]">redaction_engine.py</code>. Toggles are illustrative for this demo build.</p>
      </div>

      <!-- Card: Vault -->
      <div class="max-w-2xl bg-white border border-cream-200 rounded-xl p-5 md:p-6 shadow-sm flex flex-col gap-4 animate-fade-in">
        <h3 class="text-sm font-semibold text-charcoal-800 border-b border-cream-100 pb-3">Vault settings</h3>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <label class="text-xs font-medium text-muted">Redis URL</label>
          <input type="text" value="redis://localhost:6379/0" disabled class="font-mono text-xs text-muted p-2 rounded-lg border border-cream-200 bg-cream-50 w-full sm:w-80 cursor-not-allowed" />
        </div>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <label class="text-xs font-medium text-muted">Token TTL (seconds)</label>
          <input type="text" value="1800" disabled class="font-mono text-xs text-muted p-2 rounded-lg border border-cream-200 bg-cream-50 w-full sm:w-80 cursor-not-allowed" />
        </div>
      </div>
    `;
  }
}

customElements.define("view-settings", ViewSettings);
