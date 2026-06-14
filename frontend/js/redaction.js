/**
 * redaction.js 
 * ------------
 * Client-side mirror of the backend redaction_engine.py.
 * Detects PHI/PII via regex rules + a naive name heuristic,
 * replaces them with reversible pseudonym tokens, and exposes
 * a restore() function to reverse the substitution.
 *
 * This lets the frontend demo run standalone without a backend,
 * while staying structurally identical to the Python pipeline
 * so the two can  be swapped later.
 */

const REGEX_RULES = [
  { category: "DATE", pattern: /\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b/g },
  { category: "PHONE", pattern: /\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b/g },
  { category: "EMAIL", pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g },
  { category: "MRN", pattern: /\bMRN[:\s#-]*\d{5,10}\b/gi },
  { category: "SSN", pattern: /\b\d{3}-\d{2}-\d{4}\b/g },
  { category: "AADHAAR", pattern: /\b\d{4}\s\d{4}\s\d{4}\b/g },
  { category: "ADDRESS", pattern: /\b\d{1,5}\s[A-Za-z0-9.\s]{3,30}(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Colony|Nagar)\b/gi },
];

const NAME_PATTERN = /\b(?:Mr|Mrs|Ms|Dr|Patient)\.?\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b/g;
const PLAIN_NAME_PATTERN = /\b([A-Z][a-z]+\s[A-Z][a-z]+)\b/g;

/**
 * Find all entities (regex + name-style) in the text.
 * Returns a sorted, de-duplicated, non-overlapping list of
 * { original, category, start, end }.
 */
function detectEntities(text) {
  let entities = [];

  for (const rule of REGEX_RULES) {
    let m;
    const re = new RegExp(rule.pattern);
    while ((m = re.exec(text)) !== null) {
      entities.push({ original: m[0], category: rule.category, start: m.index, end: m.index + m[0].length });
    }
  }

  // Title-prefixed names: "Dr. Anita Verma", "Patient Rahul Sharma"
  let m;
  const nameRe = new RegExp(NAME_PATTERN);
  while ((m = nameRe.exec(text)) !== null) {
    const start = m.index + m[0].indexOf(m[1]);
    entities.push({ original: m[1], category: "NAME", start, end: start + m[1].length });
  }

  // Plain capitalized bigrams: "Rahul Sharma"
  const plainRe = new RegExp(PLAIN_NAME_PATTERN);
  while ((m = plainRe.exec(text)) !== null) {
    const start = m.index;
    const end = start + m[1].length;
    const overlaps = entities.some((e) => start >= e.start && end <= e.end);
    if (!overlaps) {
      entities.push({ original: m[1], category: "NAME", start, end });
    }
  }

  // sort by start, longest first, then drop overlaps
  entities.sort((a, b) => a.start - b.start || (b.end - b.start) - (a.end - a.start));
  const deduped = [];
  let lastEnd = -1;
  for (const e of entities) {
    if (e.start >= lastEnd) {
      deduped.push(e);
      lastEnd = e.end;
    }
  }
  return deduped;
}

/**
 * Replace detected PHI with reversible pseudonym tokens.
 * Returns { cleanText, tokenMap, entities }
 */
function redact(text) {
  const entities = detectEntities(text);
  const tokenMap = {};
  const counters = {};

  let cleanText = text;
  // Work right-to-left so earlier offsets stay valid
  for (const e of [...entities].reverse()) {
    counters[e.category] = (counters[e.category] || 0) + 1;
    let pseudonym;
    if (e.category === "NAME") {
      const idx = counters[e.category] - 1;
      const label = idx < 26 ? String.fromCharCode(65 + idx) : String(idx);
      pseudonym = `Patient ${label}`;
    } else {
      pseudonym = `${e.category}_${counters[e.category]}`;
    }
    tokenMap[pseudonym] = e.original;
    cleanText = cleanText.slice(0, e.start) + pseudonym + cleanText.slice(e.end);
  }

  return { cleanText, tokenMap, entities };
}

/**
 * Reverse the pseudonym substitution using the stored token map.
 */
function restore(text, tokenMap) {
  let restored = text;
  for (const [pseudonym, original] of Object.entries(tokenMap)) {
    restored = restored.split(pseudonym).join(original);
  }
  return restored;
}

/**
 * Generate a short pseudo-random session id for display purposes.
 */
function newSessionId() {
  return "sess_" + Math.random().toString(36).slice(2, 10);
}
