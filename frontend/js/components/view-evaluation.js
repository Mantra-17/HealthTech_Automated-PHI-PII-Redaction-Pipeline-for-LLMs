/**
 * view-evaluation.js — Custom Web Component for Model Evaluation Dashboard
 */

class ViewEvaluation extends HTMLElement {
  constructor() {
    super();
    this.notesData = null; // Keyed by NOTE_001, etc. { body, ground_truth, predictions }
    this.selectedNoteId = "NOTE_001";
    
    // Config states
    this.matchMode = "exact";
    this.strictType = true;
    this.aggregation = "micro";
    
    // Tab state
    this.activeTab = "samples"; // 'samples' or 'interactive'
  }

  connectedCallback() {
    this.renderSkeleton();
    this.setupTabListeners();
    this.setupConfigListeners();
    this.setupInteractiveCalculator();
  }

  initialize() {
    // Called when navigating to the view
    if (!this.notesData) {
      this.fetchSampleNotesData();
    } else {
      this.runEvaluation();
    }
  }

  renderSkeleton() {
    this.innerHTML = `
      <header class="view-header">
        <div>
          <h1>Model Evaluation Dashboard</h1>
          <p class="subtitle">Evaluate NLP de-identification precision, recall, and overlap diagnostics</p>
        </div>
      </header>

      <!-- Dashboard Grid -->
      <div class="eval-layout">
        
        <!-- Sidebar Controls & Config -->
        <div class="eval-sidebar">
          <div class="card config-card">
            <h3>Evaluation Parameters</h3>
            
            <div class="form-group">
              <label>Match Boundary Strategy</label>
              <div class="segmented-control">
                <button class="segment-btn active" data-config="matchMode" data-value="exact">Exact Match</button>
                <button class="segment-btn" data-config="matchMode" data-value="overlap">Overlap Match</button>
              </div>
              <p class="field-desc">Exact requires character index alignment; Overlap allows partial spans.</p>
            </div>

            <div class="form-group">
              <label>Entity Category Strictness</label>
              <div class="segmented-control">
                <button class="segment-btn active" data-config="strictType" data-value="true">Strict Type</button>
                <button class="segment-btn" data-config="strictType" data-value="false">Boundary Only</button>
              </div>
              <p class="field-desc">Strict requires matched categories; Boundary only checks span overlaps.</p>
            </div>

            <div class="form-group">
              <label>Multi-Document Aggregation</label>
              <div class="segmented-control">
                <button class="segment-btn active" data-config="aggregation" data-value="micro">Micro Avg</button>
                <button class="segment-btn" data-config="aggregation" data-value="macro">Macro Avg</button>
              </div>
              <p class="field-desc">Micro sums all entities overall; Macro averages scores per-document.</p>
            </div>
          </div>

          <!-- Quick Navigation Tabs -->
          <div class="card tab-selector-card">
            <button class="tab-btn active" data-tab="samples">
              <i class="ti ti-report-medical"></i> 20 Sample Notes Baseline
            </button>
            <button class="tab-btn" data-tab="interactive">
              <i class="ti ti-edit"></i> Interactive JSON Calculator
            </button>
          </div>
        </div>

        <!-- Main Display Content Panel -->
        <div class="eval-main">
          
          <!-- TAB 1: SAMPLES BASELINE -->
          <div id="tab-samples" class="eval-tab-content active">
            
            <!-- Global Metrics Summary -->
            <div class="metrics-row" id="global-metrics-container">
              <div class="metric-card bg-teal">
                <div class="metric-label">Precision</div>
                <div class="metric-value" id="val-precision">--%</div>
                <div class="metric-sub">True Positives / Total Detected</div>
              </div>
              <div class="metric-card bg-purple">
                <div class="metric-label">Recall</div>
                <div class="metric-value" id="val-recall">--%</div>
                <div class="metric-sub">True Positives / Ground Truth</div>
              </div>
              <div class="metric-card bg-amber">
                <div class="metric-label">F1-Score</div>
                <div class="metric-value" id="val-f1">--%</div>
                <div class="metric-sub">Harmonic Mean of P & R</div>
              </div>
              <div class="metric-card bg-gray">
                <div class="metric-label">Support (GT)</div>
                <div class="metric-value" id="val-support">--</div>
                <div class="metric-sub">Total labeled entities</div>
              </div>
            </div>

            <!-- Notes Browser & Details -->
            <div class="note-evaluator-grid">
              
              <!-- Notes List -->
              <div class="card notes-list-card">
                <h3>Select note</h3>
                <div class="notes-selector-list" id="notes-list-ul">
                  <div class="loading-spinner"><i class="ti ti-loader-2 animate-spin"></i> Loading notes...</div>
                </div>
              </div>

              <!-- Selected Note Details -->
              <div class="card note-detail-card">
                <div class="note-detail-header">
                  <h3 id="selected-note-title">Note Details</h3>
                  <div class="badge-row">
                    <span class="badge badge-tp" id="note-tp-badge">TP: --</span>
                    <span class="badge badge-fp" id="note-fp-badge">FP: --</span>
                    <span class="badge badge-fn" id="note-fn-badge">FN: --</span>
                  </div>
                </div>

                <!-- Text Highlight Output -->
                <div class="note-text-viewer">
                  <div class="viewer-legend">
                    <span class="legend-item"><span class="dot dot-green"></span> True Positive</span>
                    <span class="legend-item"><span class="dot dot-red"></span> Missed Entity (FN)</span>
                    <span class="legend-item"><span class="dot dot-purple"></span> Over-redacted (FP)</span>
                  </div>
                  <div class="highlight-body" id="note-highlight-body">
                    Select a note to view span comparisons.
                  </div>
                </div>

                <!-- Comparison Tables -->
                <div class="comparison-diagnostics-grid">
                  <div>
                    <h4>Missed Entities (False Negatives)</h4>
                    <table class="diagnostic-table">
                      <thead>
                        <tr>
                          <th>Text</th>
                          <th>Category</th>
                          <th>Span</th>
                        </tr>
                      </thead>
                      <tbody id="fn-table-body">
                        <tr><td colspan="3" class="empty-row">No misses.</td></tr>
                      </tbody>
                    </table>
                  </div>
                  <div>
                    <h4>False Positives (Over-redacted)</h4>
                    <table class="diagnostic-table">
                      <thead>
                        <tr>
                          <th>Text</th>
                          <th>Category</th>
                          <th>Span</th>
                        </tr>
                      </thead>
                      <tbody id="fp-table-body">
                        <tr><td colspan="3" class="empty-row">No false positives.</td></tr>
                      </tbody>
                    </table>
                  </div>
                </div>

              </div>

            </div>

            <!-- Class Breakdown Card -->
            <div class="card breakdown-card">
              <h3>Per-Category Metrics</h3>
              <table class="metrics-table">
                <thead>
                  <tr>
                    <th>Entity Category</th>
                    <th class="num">TP</th>
                    <th class="num">FP</th>
                    <th class="num">FN</th>
                    <th class="num">Precision</th>
                    <th class="num">Recall</th>
                    <th class="num">F1-Score</th>
                    <th class="num">Support</th>
                  </tr>
                </thead>
                <tbody id="class-metrics-body">
                  <tr><td colspan="8" class="empty-row">Run evaluation to populate category details.</td></tr>
                </tbody>
              </table>
            </div>

          </div>

          <!-- TAB 2: INTERACTIVE CALCULATOR -->
          <div id="tab-interactive" class="eval-tab-content">
            <div class="card interactive-inputs-card">
              <h3>Custom NLP Predictions Evaluator</h3>
              <p class="field-desc">Input custom Ground Truth and Predictions JSON list models to calculate accuracy metrics on the fly.</p>
              
              <div class="json-editors">
                <div class="editor-pane">
                  <div class="pane-header">
                    <label>Ground Truth JSON</label>
                    <button class="btn btn-secondary btn-xs" id="btn-format-gt">Format</button>
                  </div>
                  <textarea id="json-gt" class="code-area" spellcheck="false"></textarea>
                </div>
                <div class="editor-pane">
                  <div class="pane-header">
                    <label>Predictions JSON</label>
                    <button class="btn btn-secondary btn-xs" id="btn-format-pred">Format</button>
                  </div>
                  <textarea id="json-pred" class="code-area" spellcheck="false"></textarea>
                </div>
              </div>

              <div class="action-bar">
                <button class="btn btn-primary" id="btn-run-interactive">
                  <i class="ti ti-calculator"></i> Run custom calculation
                </button>
              </div>
            </div>

            <!-- Interactive Results Output -->
            <div id="interactive-results" style="display: none;">
              <!-- Mini cards -->
              <div class="metrics-row small-metrics">
                <div class="metric-card bg-teal">
                  <div class="metric-label">Precision</div>
                  <div class="metric-value" id="val-int-precision">100.0%</div>
                </div>
                <div class="metric-card bg-purple">
                  <div class="metric-label">Recall</div>
                  <div class="metric-value" id="val-int-recall">100.0%</div>
                </div>
                <div class="metric-card bg-amber">
                  <div class="metric-label">F1-Score</div>
                  <div class="metric-value" id="val-int-f1">100.0%</div>
                </div>
                <div class="metric-card bg-gray">
                  <div class="metric-label">Support</div>
                  <div class="metric-value" id="val-int-support">0</div>
                </div>
              </div>

              <!-- Metrics Table -->
              <div class="card breakdown-card">
                <h3>Custom Run Category Details</h3>
                <table class="metrics-table">
                  <thead>
                    <tr>
                      <th>Entity Category</th>
                      <th class="num">TP</th>
                      <th class="num">FP</th>
                      <th class="num">FN</th>
                      <th class="num">Precision</th>
                      <th class="num">Recall</th>
                      <th class="num">F1-Score</th>
                      <th class="num">Support</th>
                    </tr>
                  </thead>
                  <tbody id="interactive-class-metrics-body">
                    <tr><td colspan="8" class="empty-row">No interactive results.</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>

        </div>

      </div>
    `;
  }

  setupTabListeners() {
    this.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        this.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
        this.querySelectorAll(".eval-tab-content").forEach((c) => c.classList.remove("active"));
        
        btn.classList.add("active");
        const selectedTab = btn.dataset.tab;
        this.activeTab = selectedTab;
        this.querySelector(`#tab-${selectedTab}`).classList.add("active");
        
        if (selectedTab === "samples") {
          this.runEvaluation();
        }
      });
    });
  }

  setupConfigListeners() {
    this.querySelectorAll(".segment-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const configName = btn.dataset.config;
        let value = btn.dataset.value;
        if (value === "true") value = true;
        if (value === "false") value = false;
        
        // Remove active from siblings in this segmented control
        btn.parentElement.querySelectorAll(".segment-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        
        // Update state
        this[configName] = value;
        
        // Re-run evaluation
        if (this.activeTab === "samples") {
          this.runEvaluation();
        } else {
          this.runInteractiveEvaluation();
        }
      });
    });
  }

  setupInteractiveCalculator() {
    // Fill textareas with prefilled default JSONs
    const defaultGT = [
      { "start": 8, "end": 18, "type": "PERSON", "text": "John Smith" },
      { "start": 35, "end": 45, "type": "DATE", "text": "05/06/2026" }
    ];
    const defaultPred = [
      { "start": 8, "end": 18, "type": "PERSON", "text": "John Smith" },
      { "start": 35, "end": 44, "type": "DATE", "text": "05/06/202" }
    ];

    this.querySelector("#json-gt").value = JSON.stringify(defaultGT, null, 2);
    this.querySelector("#json-pred").value = JSON.stringify(defaultPred, null, 2);

    this.querySelector("#btn-run-interactive").addEventListener("click", () => {
      this.runInteractiveEvaluation();
    });

    this.querySelector("#btn-format-gt").addEventListener("click", () => {
      this.formatTextareaJson("#json-gt");
    });

    this.querySelector("#btn-format-pred").addEventListener("click", () => {
      this.formatTextareaJson("#json-pred");
    });
  }

  formatTextareaJson(selector) {
    const area = this.querySelector(selector);
    try {
      const parsed = JSON.parse(area.value);
      area.value = JSON.stringify(parsed, null, 2);
    } catch (err) {
      alert("Invalid JSON format: " + err.message);
    }
  }

  async fetchSampleNotesData() {
    const container = this.querySelector("#notes-list-ul");
    container.innerHTML = `<div class="loading-spinner"><i class="ti ti-loader-2 animate-spin"></i> Fetching ground truth and predictions...</div>`;
    
    try {
      const res = await API.getEvaluationSampleNotes();
      this.notesData = res.notes;
      this.runEvaluation();
    } catch (err) {
      container.innerHTML = `<div class="error-msg"><i class="ti ti-alert-triangle"></i> Failed to load sample notes evaluation. Ensure backend is running.</div>`;
      console.error(err);
    }
  }

  async runEvaluation() {
    if (!this.notesData) return;

    // 1. Separate ground truths and predictions lists
    const gtDocs = {};
    const predDocs = {};
    for (const [noteId, data] of Object.entries(this.notesData)) {
      gtDocs[noteId] = data.ground_truth;
      predDocs[noteId] = data.predictions;
    }

    try {
      // 2. Invoke API to calculate overall stats
      const report = await API.evaluate(gtDocs, predDocs, this.matchMode, this.strictType, this.aggregation);
      
      // 3. Render Dashboard Metrics
      const gm = report.global_metrics;
      this.querySelector("#val-precision").textContent = (gm.precision * 100).toFixed(2) + "%";
      this.querySelector("#val-recall").textContent = (gm.recall * 100).toFixed(2) + "%";
      this.querySelector("#val-f1").textContent = (gm.f1 * 100).toFixed(2) + "%";
      this.querySelector("#val-support").textContent = gm.support;

      // 4. Render Category Table
      this.renderCategoryTable(report.class_metrics, "#class-metrics-body");

      // 5. Render Notes list selectors
      this.renderNotesList();

      // 6. Highlight selected note
      this.highlightSelectedNote();

    } catch (err) {
      console.error("Evaluation run failed:", err);
    }
  }

  async runInteractiveEvaluation() {
    const gtArea = this.querySelector("#json-gt").value.trim();
    const predArea = this.querySelector("#json-pred").value.trim();
    
    let gt = [];
    let pred = [];
    try {
      gt = JSON.parse(gtArea);
    } catch (e) {
      alert("Invalid Ground Truth JSON: " + e.message);
      return;
    }

    try {
      pred = JSON.parse(predArea);
    } catch (e) {
      alert("Invalid Predictions JSON: " + e.message);
      return;
    }

    try {
      const report = await API.evaluate(gt, pred, this.matchMode, this.strictType, "micro");
      const gm = report.global_metrics;

      this.querySelector("#val-int-precision").textContent = (gm.precision * 100).toFixed(1) + "%";
      this.querySelector("#val-int-recall").textContent = (gm.recall * 100).toFixed(1) + "%";
      this.querySelector("#val-int-f1").textContent = (gm.f1 * 100).toFixed(1) + "%";
      this.querySelector("#val-int-support").textContent = gm.support;

      this.renderCategoryTable(report.class_metrics, "#interactive-class-metrics-body");
      
      this.querySelector("#interactive-results").style.display = "block";
    } catch (err) {
      alert("Interactive evaluation failed: " + err.message);
    }
  }

  renderCategoryTable(classMetrics, bodySelector) {
    const tbody = this.querySelector(bodySelector);
    if (!classMetrics || Object.keys(classMetrics).length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="empty-row">No entities matched criteria.</td></tr>`;
      return;
    }

    let rowsHtml = "";
    const sortedCategories = Object.keys(classMetrics).sort();
    
    for (const cat of sortedCategories) {
      const metrics = classMetrics[cat];
      rowsHtml += `
        <tr>
          <td><strong>${cat}</strong></td>
          <td class="num">${metrics.tp}</td>
          <td class="num">${metrics.fp}</td>
          <td class="num">${metrics.fn}</td>
          <td class="num">${(metrics.precision * 100).toFixed(1)}%</td>
          <td class="num">${(metrics.recall * 100).toFixed(1)}%</td>
          <td class="num">${(metrics.f1 * 100).toFixed(1)}%</td>
          <td class="num">${metrics.support}</td>
        </tr>
      `;
    }

    tbody.innerHTML = rowsHtml;
  }

  renderNotesList() {
    const container = this.querySelector("#notes-list-ul");
    let html = "";
    
    const noteIds = Object.keys(this.notesData).sort();
    for (const noteId of noteIds) {
      const activeClass = noteId === this.selectedNoteId ? "active" : "";
      html += `
        <div class="note-li-item ${activeClass}" data-note-id="${noteId}">
          <span class="note-name">${noteId}</span>
          <span class="note-stat-tag">GT: ${this.notesData[noteId].ground_truth.length}</span>
        </div>
      `;
    }

    container.innerHTML = html;

    // Attach click listeners
    container.querySelectorAll(".note-li-item").forEach((item) => {
      item.addEventListener("click", () => {
        this.selectedNoteId = item.dataset.noteId;
        this.querySelector(".note-li-item.active")?.classList.remove("active");
        item.classList.add("active");
        this.highlightSelectedNote();
      });
    });
  }

  async highlightSelectedNote() {
    if (!this.notesData || !this.selectedNoteId) return;

    const note = this.notesData[this.selectedNoteId];
    this.querySelector("#selected-note-title").textContent = `Analysis of ${this.selectedNoteId}`;

    const gtList = note.ground_truth;
    const predList = note.predictions;

    try {
      // Run single document alignment calculation to find TP, FP, FN
      const report = await API.evaluate(gtList, predList, this.matchMode, this.strictType, "micro");
      
      // We also evaluate single doc alignment using backend to get exactly which spans matched/missed
      // To get detailed alignment for highlighting, we can run local or backend matching.
      // Let's implement local alignment computation matching NLPEvaluator.evaluate_single_doc so we can highlight spans in Javascript!
      const { matched, unmatchedGt, unmatchedPred } = this.calculateLocalAlignment(gtList, predList);
      
      // Update badges
      this.querySelector("#note-tp-badge").textContent = `TP: ${matched.length}`;
      this.querySelector("#note-fp-badge").textContent = `FP: ${unmatchedPred.length}`;
      this.querySelector("#note-fn-badge").textContent = `FN: ${unmatchedGt.length}`;

      // Populate diagnostic tables
      this.renderDiagnosticTables(unmatchedGt, unmatchedPred);

      // Render highlighted body
      this.renderHighlightedBody(note.body, matched, unmatchedGt, unmatchedPred);

    } catch (err) {
      console.error(err);
    }
  }

  calculateLocalAlignment(gtList, predList) {
    const overlaps = (a, b) => a.start < b.end && b.start < a.end;
    const computeIoU = (a, b) => {
      const intersection = Math.max(0, Math.min(a.end, b.end) - Math.max(a.start, b.start));
      const union = (a.end - a.start) + (b.end - b.start) - intersection;
      return union > 0 ? intersection / union : 0;
    };

    const gtCopy = gtList.map((g, idx) => ({ ...g, _origIdx: idx }));
    const predCopy = predList.map((p, idx) => ({ ...p, _origIdx: idx }));

    // Generate candidates
    const candidates = [];
    for (const gt of gtCopy) {
      for (const pred of predCopy) {
        if (this.strictType) {
          if (String(gt.type).toLowerCase() !== String(pred.type).toLowerCase()) continue;
        }

        let isMatch = false;
        let score = 0;
        if (this.matchMode === "exact") {
          if (gt.start === pred.start && gt.end === pred.end) {
            isMatch = true;
            score = 1.0;
          }
        } else {
          if (overlaps(gt, pred)) {
            isMatch = true;
            score = computeIoU(gt, pred);
          }
        }

        if (isMatch) {
          candidates.push({ gt, pred, score });
        }
      }
    }

    // Sort candidates
    candidates.sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      return a.gt.start - b.gt.start;
    });

    const matchedGt = new Set();
    const matchedPred = new Set();
    const matched = [];

    for (const c of candidates) {
      if (!matchedGt.has(c.gt._origIdx) && !matchedPred.has(c.pred._origIdx)) {
        matchedGt.add(c.gt._origIdx);
        matchedPred.add(c.pred._origIdx);
        matched.push(c);
      }
    }

    const unmatchedGt = gtCopy.filter(g => !matchedGt.has(g._origIdx));
    const unmatchedPred = predCopy.filter(p => !matchedPred.has(p._origIdx));

    return { matched, unmatchedGt, unmatchedPred };
  }

  renderDiagnosticTables(unmatchedGt, unmatchedPred) {
    const fnBody = this.querySelector("#fn-table-body");
    const fpBody = this.querySelector("#fp-table-body");

    if (unmatchedGt.length === 0) {
      fnBody.innerHTML = `<tr><td colspan="3" class="empty-row">No missed entities (100% recall).</td></tr>`;
    } else {
      fnBody.innerHTML = unmatchedGt.map(g => `
        <tr>
          <td><code class="val-code">${g.text || ""}</code></td>
          <td><span class="type-tag bg-coral-light">${g.type.toUpperCase()}</span></td>
          <td class="mono-span">${g.start}-${g.end}</td>
        </tr>
      `).join("");
    }

    if (unmatchedPred.length === 0) {
      fpBody.innerHTML = `<tr><td colspan="3" class="empty-row">No over-redactions (100% precision).</td></tr>`;
    } else {
      fpBody.innerHTML = unmatchedPred.map(p => `
        <tr>
          <td><code class="val-code">${p.text || ""}</code></td>
          <td><span class="type-tag bg-purple-light">${p.type.toUpperCase()}</span></td>
          <td class="mono-span">${p.start}-${p.end}</td>
        </tr>
      `).join("");
    }
  }

  renderHighlightedBody(body, matched, unmatchedGt, unmatchedPred) {
    const container = this.querySelector("#note-highlight-body");
    
    // Build spans to highlight
    const highlightSpans = [];
    
    for (const m of matched) {
      // True Positive
      // We can use ground truth coordinates, or average, or show GT vs Pred overlap. Let's use GT span to highlight
      highlightSpans.push({
        start: m.gt.start,
        end: m.gt.end,
        type: "tp",
        label: `${m.gt.type.toUpperCase()}`,
        origVal: m.gt.text
      });
    }

    for (const g of unmatchedGt) {
      // False Negative
      highlightSpans.push({
        start: g.start,
        end: g.end,
        type: "fn",
        label: `${g.type.toUpperCase()} (MISSED)`,
        origVal: g.text
      });
    }

    for (const p of unmatchedPred) {
      // False Positive
      highlightSpans.push({
        start: p.start,
        end: p.end,
        type: "fp",
        label: `${p.type.toUpperCase()} (FALSE POS)`,
        origVal: p.text
      });
    }

    // Sort spans, filtering overlapping ones to prevent markup nest errors
    highlightSpans.sort((a, b) => a.start - b.start || (b.end - a.end));
    
    const nonOverlapping = [];
    let lastEnd = -1;
    for (const span of highlightSpans) {
      if (span.start >= lastEnd) {
        nonOverlapping.push(span);
        lastEnd = span.end;
      }
    }

    // Splice string
    let htmlResult = "";
    let currentIndex = 0;
    
    for (const span of nonOverlapping) {
      // Text before highlight
      htmlResult += this.escapeHtml(body.substring(currentIndex, span.start));
      
      // Highlight element
      const highlightClass = `span-hl-${span.type}`;
      htmlResult += `
        <span class="span-highlight ${highlightClass}">
          ${this.escapeHtml(body.substring(span.start, span.end))}
          <span class="span-hl-tag">${span.label}</span>
        </span>
      `;
      
      currentIndex = span.end;
    }
    
    // Remaining text
    htmlResult += this.escapeHtml(body.substring(currentIndex));
    container.innerHTML = htmlResult;
  }

  escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}

customElements.define("view-evaluation", ViewEvaluation);
