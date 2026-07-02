/**
 * view-vault.js — Custom Web Component for Vault Sessions View
 */

class ViewVault extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <header class="mb-6 md:mb-8 pb-4 border-b border-cream-200">
        <h1>Vault sessions</h1>
        <p class="text-sm text-muted mt-1">Active token maps stored in Redis</p>
      </header>

      <!-- Metrics Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl">
        <div class="bg-white border border-cream-200 rounded-xl p-5 shadow-sm">
          <span class="block text-[10px] text-muted font-bold uppercase tracking-wider">Active sessions</span>
          <span class="block text-3xl font-semibold text-charcoal-800 mt-2" id="metric-sessions">0</span>
        </div>
        <div class="bg-white border border-cream-200 rounded-xl p-5 shadow-sm">
          <span class="block text-[10px] text-muted font-bold uppercase tracking-wider">Tokens stored</span>
          <span class="block text-3xl font-semibold text-charcoal-800 mt-2" id="metric-tokens">0</span>
        </div>
        <div class="bg-white border border-cream-200 rounded-xl p-5 shadow-sm">
          <span class="block text-[10px] text-muted font-bold uppercase tracking-wider">Session TTL</span>
          <span class="block text-3xl font-semibold text-charcoal-800 mt-2">30 min</span>
        </div>
      </div>

      <!-- Responsive Data Table -->
      <div class="w-full overflow-x-auto bg-white border border-cream-200 rounded-xl shadow-sm mt-8">
        <table class="w-full text-left border-collapse text-sm">
          <thead>
            <tr>
              <th class="px-5 py-4 bg-cream-50 text-muted font-semibold text-[11px] uppercase tracking-wider border-b border-cream-200">Session ID</th>
              <th class="px-5 py-4 bg-cream-50 text-muted font-semibold text-[11px] uppercase tracking-wider border-b border-cream-200">Tokens</th>
              <th class="px-5 py-4 bg-cream-50 text-muted font-semibold text-[11px] uppercase tracking-wider border-b border-cream-200">Created</th>
              <th class="px-5 py-4 bg-cream-50 text-muted font-semibold text-[11px] uppercase tracking-wider border-b border-cream-200">Expires in</th>
              <th class="px-5 py-4 bg-cream-50 text-muted font-semibold text-[11px] uppercase tracking-wider border-b border-cream-200"></th>
            </tr>
          </thead>
          <tbody id="vault-table-body" class="divide-y divide-cream-100">
            <tr>
              <td colspan="5" class="px-5 py-8 text-center text-xs text-tertiary">No sessions yet. Run a redaction to create one.</td>
            </tr>
          </tbody>
        </table>
      </div>
    `;
  }
}

customElements.define("view-vault", ViewVault);
