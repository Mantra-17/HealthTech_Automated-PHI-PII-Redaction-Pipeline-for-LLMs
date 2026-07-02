/**
 * view-proxy.js — Custom Web Component for Proxy View
 */

class ViewProxy extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <header class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 md:mb-8 pb-4 border-b border-cream-200">
        <div>
          <h1 class="text-2xl font-semibold text-charcoal-800">Clinical note proxy</h1>
          <p class="text-sm text-muted mt-1">Submit a note. PHI never leaves this boundary.</p>
        </div>
        <div class="inline-flex items-center gap-2 self-start bg-teal-50 text-teal-800 text-xs font-semibold px-3 py-1.5 rounded-lg border border-teal-800/10 shadow-sm">
          <i class="ti ti-shield-check text-base text-teal-600"></i>
          <span>Org control boundary</span>
        </div>
      </header>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- Input -->
        <div class="bg-white border border-cream-200 rounded-xl p-5 md:p-6 shadow-sm flex flex-col gap-4">
          <div class="flex items-center justify-between">
            <h3 class="flex items-center gap-2 text-sm font-semibold text-charcoal-800">
              <i class="ti ti-file-text text-base text-muted"></i> Original note (doctor input)
            </h3>
            <span class="text-[10px] font-semibold px-2 py-0.5 rounded bg-coral-50 text-coral-800 border border-coral-800/10">Contains PHI</span>
          </div>
          <textarea id="input-note" rows="9" class="w-full min-h-[160px] font-mono text-[13px] leading-relaxed p-4 border border-cream-200 rounded-lg bg-cream-50 text-charcoal-800 focus:outline-none focus:ring-2 focus:ring-teal-600 focus:bg-white transition-all duration-200 resize-y" placeholder="Paste or type the clinical note here...">Patient Rahul Sharma, DOB 14/03/1985, MRN: 4582193, presented on 12/06/2026 with persistent cough and fever (101.2 F). Contact: rahul.sharma@gmail.com, +91 98765 43210. Address: 22 MG Road, Jodhpur. Dr. Anita Verma recommends a chest X-ray and a 5-day course of azithromycin. Aadhaar 1234 5678 9012.</textarea>
          <div class="flex gap-3">
            <button id="btn-redact" class="inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg bg-teal-600 text-white hover:bg-teal-700 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm">
              <i class="ti ti-scan text-base"></i> Run redaction
            </button>
            <button id="btn-clear" class="inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-lg border border-cream-200 bg-white text-charcoal-800 hover:bg-cream-50 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200">
              <i class="ti ti-trash text-base"></i> Clear
            </button>
          </div>
        </div>

        <!-- Redacted -->
        <div class="bg-white border border-cream-200 rounded-xl p-5 md:p-6 shadow-sm flex flex-col gap-4">
          <div class="flex items-center justify-between">
            <h3 class="flex items-center gap-2 text-sm font-semibold text-charcoal-800">
              <i class="ti ti-eraser text-base text-muted"></i> Redacted (sent to external AI)
            </h3>
            <span class="text-[10px] font-semibold px-2 py-0.5 rounded bg-teal-50 text-teal-800 border border-teal-800/10">PHI removed</span>
          </div>
          <div id="output-redacted" class="output-box placeholder">
            Run redaction to see the de-identified version of this note.
          </div>
          <div>
            <button id="btn-send-ai" class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-semibold rounded-lg bg-teal-600 text-white hover:bg-teal-700 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 shadow-sm" disabled>
              <i class="ti ti-sparkles text-base"></i> Send to AI assistant
            </button>
          </div>
        </div>

        <!-- Token map -->
        <div class="bg-white border border-cream-200 rounded-xl p-5 md:p-6 shadow-sm flex flex-col gap-4">
          <div class="flex items-center justify-between">
            <h3 class="flex items-center gap-2 text-sm font-semibold text-charcoal-800">
              <i class="ti ti-key text-base text-muted"></i> Vault token map
            </h3>
            <span class="text-[10px] font-semibold px-2 py-0.5 rounded bg-cream-100 text-muted border border-cream-200">Redis (TTL 30 min)</span>
          </div>
          <div id="token-map" class="token-map placeholder">
            No active session. Token mappings will appear here after redaction.
          </div>
        </div>

        <!-- AI response -->
        <div class="bg-white border border-cream-200 rounded-xl p-5 md:p-6 shadow-sm flex flex-col gap-4">
          <div class="flex items-center justify-between">
            <h3 class="flex items-center gap-2 text-sm font-semibold text-charcoal-800">
              <i class="ti ti-robot text-base text-muted"></i> AI response (restored)
            </h3>
            <span class="text-[10px] font-semibold px-2 py-0.5 rounded bg-purple-50 text-purple-800 border border-purple-800/10">Identities restored</span>
          </div>
          <div id="output-final" class="output-box placeholder">
            The AI's response, with patient identity restored, will appear here.
          </div>
        </div>

      </div>
    `;
  }
}

customElements.define("view-proxy", ViewProxy);
