/**
 * view-pipeline.js — Custom Web Component for Pipeline Overview View
 */

class ViewPipeline extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <header class="mb-6 md:mb-8 pb-4 border-b border-cream-200">
        <h1>Pipeline overview</h1>
        <p class="text-sm text-muted mt-1">How a note moves through the redaction proxy</p>
      </header>

      <div class="max-w-2xl bg-white border border-cream-200 rounded-xl p-5 md:p-8 shadow-sm flex flex-col gap-2">
        <div class="flex gap-4 p-4 rounded-xl border border-cream-50 bg-cream-50/50 hover:bg-cream-50 hover:border-cream-200 transition-all duration-200 group">
          <div class="w-10 h-10 flex-shrink-0 rounded-lg flex items-center justify-center bg-cream-100 text-muted group-hover:bg-white transition-colors text-lg"><i class="ti ti-stethoscope"></i></div>
          <div>
            <h4 class="text-sm font-semibold text-charcoal-800">1. Doctor submits note</h4>
            <p class="text-xs text-muted leading-relaxed mt-1">Clinical note sent to the internal proxy API. Never leaves the org boundary unredacted.</p>
          </div>
        </div>
        <div class="flex justify-center py-1 text-tertiary"><i class="ti ti-arrow-down text-lg"></i></div>

        <div class="flex gap-4 p-4 rounded-xl border border-cream-50 bg-cream-50/50 hover:bg-cream-50 hover:border-cream-200 transition-all duration-200 group">
          <div class="w-10 h-10 flex-shrink-0 rounded-lg flex items-center justify-center bg-coral-50 text-coral-800 group-hover:bg-white transition-colors text-lg"><i class="ti ti-scan"></i></div>
          <div>
            <h4 class="text-sm font-semibold text-charcoal-800">2. Redaction engine</h4>
            <p class="text-xs text-muted leading-relaxed mt-1">Regex rules + NLP entity detection run in parallel to catch names, dates, MRNs, contact details, addresses.</p>
          </div>
        </div>
        <div class="flex justify-center py-1 text-tertiary"><i class="ti ti-arrow-down text-lg"></i></div>

        <div class="flex gap-4 p-4 rounded-xl border border-cream-50 bg-cream-50/50 hover:bg-cream-50 hover:border-cream-200 transition-all duration-200 group">
          <div class="w-10 h-10 flex-shrink-0 rounded-lg flex items-center justify-center bg-vault-50 text-vault-800 group-hover:bg-white transition-colors text-lg"><i class="ti ti-lock"></i></div>
          <div>
            <h4 class="text-sm font-semibold text-charcoal-800">3. Vault stores token map</h4>
            <p class="text-xs text-muted leading-relaxed mt-1">"Patient A" ↔ "Rahul Sharma" stored securely in Redis with a session TTL.</p>
          </div>
        </div>
        <div class="flex justify-center py-1 text-tertiary"><i class="ti ti-arrow-down text-lg"></i></div>

        <div class="flex gap-4 p-4 rounded-xl border border-cream-50 bg-cream-50/50 hover:bg-cream-50 hover:border-cream-200 transition-all duration-200 group">
          <div class="w-10 h-10 flex-shrink-0 rounded-lg flex items-center justify-center bg-teal-50 text-teal-800 group-hover:bg-white transition-colors text-lg"><i class="ti ti-cloud-upload"></i></div>
          <div>
            <h4 class="text-sm font-semibold text-charcoal-800">4. Clean text sent to external AI</h4>
            <p class="text-xs text-muted leading-relaxed mt-1">No real names, dates, or identifiers leave the system. Only pseudonymized text is sent.</p>
          </div>
        </div>
        <div class="flex justify-center py-1 text-tertiary"><i class="ti ti-arrow-down text-lg"></i></div>

        <div class="flex gap-4 p-4 rounded-xl border border-cream-50 bg-cream-50/50 hover:bg-cream-50 hover:border-cream-200 transition-all duration-200 group">
          <div class="w-10 h-10 flex-shrink-0 rounded-lg flex items-center justify-center bg-teal-50 text-teal-800 group-hover:bg-white transition-colors text-lg"><i class="ti ti-message-reply"></i></div>
          <div>
            <h4 class="text-sm font-semibold text-charcoal-800">5. AI responds with pseudonyms</h4>
            <p class="text-xs text-muted leading-relaxed mt-1">The external model's response references "Patient A" and other tokens only.</p>
          </div>
        </div>
        <div class="flex justify-center py-1 text-tertiary"><i class="ti ti-arrow-down text-lg"></i></div>

        <div class="flex gap-4 p-4 rounded-xl border border-cream-50 bg-cream-50/50 hover:bg-cream-50 hover:border-cream-200 transition-all duration-200 group">
          <div class="w-10 h-10 flex-shrink-0 rounded-lg flex items-center justify-center bg-purple-50 text-purple-800 group-hover:bg-white transition-colors text-lg"><i class="ti ti-replace"></i></div>
          <div>
            <h4 class="text-sm font-semibold text-charcoal-800">6. Vault restores identities</h4>
            <p class="text-xs text-muted leading-relaxed mt-1">Pseudonyms swapped back to real patient details before the result reaches the doctor.</p>
          </div>
        </div>
      </div>
    `;
  }
}

customElements.define("view-pipeline", ViewPipeline);
