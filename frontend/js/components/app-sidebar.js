/**
 * app-sidebar.js — Custom Web Component for Sidebar
 */

class AppSidebar extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <aside class="w-full md:w-64 bg-white border-b md:border-b-0 md:border-r border-cream-200 flex flex-col md:h-screen md:sticky md:top-0 p-4 md:p-6 transition-all duration-300">
        <!-- Brand / Header -->
        <div class="flex items-center justify-between border-b border-cream-200 pb-4 mb-4 md:mb-6">
          <div class="flex items-center gap-2.5 font-semibold text-[17px] text-teal-800">
            <i class="ti ti-shield-lock text-2xl text-teal-600"></i>
            <span>PHI Redaction Proxy</span>
          </div>
          <!-- Hamburger menu button (Mobile only) -->
          <button id="mobile-nav-toggle" class="md:hidden flex items-center justify-center p-2 rounded-lg text-muted hover:bg-cream-50 hover:text-charcoal-800 focus:outline-none transition-all duration-200">
            <i class="ti ti-menu-2 text-xl" id="menu-icon"></i>
          </button>
        </div>
        
        <!-- Navigation Links -->
        <nav id="sidebar-nav" class="hidden md:flex flex-col gap-1.5 flex-1">
          <a href="#" class="nav-item flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm text-muted hover:bg-cream-50 hover:text-charcoal-800 transition-all duration-150 active" data-view="proxy">
            <i class="ti ti-message-2 text-lg"></i> New note
          </a>
          <a href="#" class="nav-item flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm text-muted hover:bg-cream-50 hover:text-charcoal-800 transition-all duration-150" data-view="pipeline">
            <i class="ti ti-route text-lg"></i> Pipeline
          </a>
          <a href="#" class="nav-item flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm text-muted hover:bg-cream-50 hover:text-charcoal-800 transition-all duration-150" data-view="vault">
            <i class="ti ti-lock text-lg"></i> Vault sessions
          </a>
          <a href="#" class="nav-item flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm text-muted hover:bg-cream-50 hover:text-charcoal-800 transition-all duration-150" data-view="logs">
            <i class="ti ti-list-details text-lg"></i> Audit log
          </a>
          <a href="#" class="nav-item flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm text-muted hover:bg-cream-50 hover:text-charcoal-800 transition-all duration-150" data-view="settings">
            <i class="ti ti-settings text-lg"></i> Settings
          </a>
        </nav>
        
        <!-- Clinician Profile Card -->
        <div class="sidebar-user mt-auto mb-4 p-3 rounded-xl bg-cream-50 border border-cream-200 flex items-center gap-3 transition-all duration-300 hover:bg-teal-50 hover:border-teal-600 group" id="sidebar-profile-card" style="display: none;">
          <img class="w-9 h-9 rounded-full object-cover bg-teal-50 text-teal-800 flex items-center justify-center text-lg flex-shrink-0 border border-cream-200 group-hover:bg-white transition-colors duration-200" id="sidebar-user-avatar" src="img/dr_alex_profile.png" alt="Dr. Alex Carter" />
          <div class="min-w-0 flex-1">
            <div class="text-xs font-semibold text-charcoal-800 truncate" id="sidebar-user-name">Dr. Alex Carter, MD</div>
            <div class="flex items-center mt-0.5">
              <span class="text-[10px] font-medium text-teal-800 bg-teal-50 px-1.5 py-0.5 rounded border border-teal-800/10 group-hover:bg-white transition-colors duration-200" id="sidebar-user-role">HIPAA Full Access</span>
            </div>
            <a href="#" class="inline-block text-[10px] text-muted underline hover:text-teal-600 mt-1 transition-colors duration-150" id="btn-logout">Switch Profile</a>
          </div>
        </div>

        <!-- Connection Badges -->
        <div class="sidebar-footer hidden md:flex flex-col gap-2 pt-4 border-t border-cream-200">
          <div class="flex items-center gap-2 text-xs text-muted">
            <span class="w-2 h-2 rounded-full bg-green-600"></span> Vault: connected
          </div>
          <div class="flex items-center gap-2 text-xs text-muted">
            <span class="w-2 h-2 rounded-full bg-green-600"></span> Engine: ready
          </div>
        </div>
      </aside>
    `;

    // Interactive hamburger menu toggle
    const toggleBtn = this.querySelector("#mobile-nav-toggle");
    const nav = this.querySelector("#sidebar-nav");
    const menuIcon = this.querySelector("#menu-icon");
    if (toggleBtn && nav) {
      toggleBtn.addEventListener("click", () => {
        const isHidden = nav.classList.contains("hidden");
        if (isHidden) {
          nav.classList.remove("hidden");
          nav.classList.add("flex");
          menuIcon.className = "ti ti-x text-xl";
        } else {
          nav.classList.remove("flex");
          nav.classList.add("hidden");
          menuIcon.className = "ti ti-menu-2 text-xl";
        }
      });
      
      // Auto-collapse mobile navigation menu when a link is clicked
      nav.querySelectorAll(".nav-item").forEach((item) => {
        item.addEventListener("click", () => {
          if (window.innerWidth < 768) {
            nav.classList.remove("flex");
            nav.classList.add("hidden");
            menuIcon.className = "ti ti-menu-2 text-xl";
          }
        });
      });
    }
  }
}

customElements.define("app-sidebar", AppSidebar);
