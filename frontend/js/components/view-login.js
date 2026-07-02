/**
 * view-login.js — Custom Web Component for Login Screen
 */

class ViewLogin extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <div class="fixed inset-0 bg-cream-100 flex items-center justify-center z-[1000] p-4 sm:p-6">
        <div class="bg-white border border-cream-200 rounded-2xl max-w-2xl w-full p-6 sm:p-10 shadow-premium animate-fade-in">
          <div class="flex items-center gap-2.5 font-semibold text-lg text-teal-800 mb-6">
            <i class="ti ti-shield-lock text-3xl text-teal-600"></i>
            <span>HealthTech PHI Redaction Gate</span>
          </div>
          <h2 class="text-2xl font-semibold text-charcoal-800 mb-2">Access Gateway Authorization</h2>
          <p class="text-sm text-muted leading-relaxed mb-8">Please select a clinician profile to log in to the EHR-connected proxy. Access is logged for compliance auditing.</p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Full Access Profile -->
            <div class="profile-select-card bg-cream-50 hover:bg-white border border-cream-200 hover:border-teal-600 rounded-xl p-5 cursor-pointer transition-all duration-300 hover:shadow-premium-hover hover:-translate-y-1 flex flex-col gap-4 group" data-user="dr_alex">
              <div class="flex justify-between items-center">
                <img class="w-11 h-11 rounded-full object-cover border border-cream-200" src="img/dr_alex_profile.png" alt="Dr. Alex Carter" />
                <span class="text-[10px] font-semibold px-2 py-0.5 rounded bg-teal-50 text-teal-800 border border-teal-800/10 transition-colors">Full HIPAA Access</span>
              </div>
              <div>
                <h3 class="text-sm font-semibold text-charcoal-800">Dr. Alex Carter, MD</h3>
                <p class="text-xs text-muted font-medium mt-0.5">Chief Medical Director</p>
                <p class="text-xs text-tertiary leading-relaxed mt-2.5">Full de-identification & identity restoration privileges. All clinical summaries restored.</p>
              </div>
            </div>

            <!-- Restricted Access Profile -->
            <div class="profile-select-card bg-cream-50 hover:bg-white border border-cream-200 hover:border-coral-500 rounded-xl p-5 cursor-pointer transition-all duration-300 hover:shadow-premium-hover hover:-translate-y-1 flex flex-col gap-4 group" data-user="jash_shah">
              <div class="flex justify-between items-center">
                <div class="w-11 h-11 rounded-full flex items-center justify-center bg-cream-200 border border-cream-300 text-muted group-hover:bg-cream-100 transition-colors text-xl">
                  <i class="ti ti-user"></i>
                </div>
                <span class="text-[10px] font-semibold px-2 py-0.5 rounded bg-coral-50 text-coral-800 border border-coral-800/10 transition-colors">Restricted Access</span>
              </div>
              <div>
                <h3 class="text-sm font-semibold text-charcoal-800">Jash Shah</h3>
                <p class="text-xs text-muted font-medium mt-0.5">Research Assistant</p>
                <p class="text-xs text-tertiary leading-relaxed mt-2.5">De-identification privileges only. Stored patient identities remain redacted in AI summaries.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }
}

customElements.define("view-login", ViewLogin);
