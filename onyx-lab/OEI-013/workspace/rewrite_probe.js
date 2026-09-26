#!/usr/bin/env node
/*
 * OEI-013 — probe the SHIPPED question-rewrite logic.
 *
 * The point of this file is that it does not re-implement the rewrite. It reads
 * `demos/spa/app.js` and evaluates the real `CONSULTING_QUESTION_LEXICON` +
 * `rewriteConsultingQuestion` out of it, so the evidence describes the code
 * that actually ships. A copy of the logic here would prove nothing about the
 * SPA.
 *
 * It asserts the extraction boundary exists before using it — if the markers
 * move, this fails loudly instead of silently probing an empty string.
 *
 * Usage:  node rewrite_probe.js            # default question + chips
 *         node rewrite_probe.js "任意问题"   # one-off question
 */
"use strict";
const fs = require("fs");
const path = require("path");

const APP_JS = process.env.SPA_APP_JS ||
  "/mnt/d/Projects/domainAgentECE/ece/demos/spa/app.js";
const INDEX_HTML = process.env.SPA_INDEX_HTML ||
  "/mnt/d/Projects/domainAgentECE/ece/demos/spa/index.html";

const src = fs.readFileSync(APP_JS, "utf8");

const START = "var CONSULTING_QUESTION_LEXICON";
const END = "function setConsultingRewriteNote";
const i = src.indexOf(START);
const j = src.indexOf(END);
if (i < 0 || j < 0 || j <= i) {
  console.error("FATAL: extraction markers not found in " + APP_JS);
  console.error("  START=" + START + " -> " + i);
  console.error("  END  =" + END + " -> " + j);
  process.exit(2);
}
const slice = src.slice(i, j);
if (slice.indexOf("rewriteConsultingQuestion") < 0) {
  console.error("FATAL: extracted slice has no rewriteConsultingQuestion");
  process.exit(2);
}

// eslint-disable-next-line no-eval
const factory = new Function(slice + "\nreturn { lexicon: CONSULTING_QUESTION_LEXICON,"
  + " rewrite: rewriteConsultingQuestion, maxTerms: CONSULTING_REWRITE_MAX_TERMS };");
const mod = factory();

// The default question is read out of the SPA source too, so the probe cannot
// drift from what the view actually pre-fills.
const dq = /var CONSULTING_DEMO_QUESTION = "([^"]+)"/.exec(src);
if (!dq) { console.error("FATAL: CONSULTING_DEMO_QUESTION not found"); process.exit(2); }
const demoQuestion = dq[1];

// Chips: the questions the audience can click in act one.
const chips = [];
const chipRe = /class="chip"[^>]*data-question="([^"]+)"/g;
const html = fs.readFileSync(INDEX_HTML, "utf8");
let m;
while ((m = chipRe.exec(html)) !== null) chips.push(m[1]);

const argv = process.argv.slice(2);
const cases = argv.length > 0
  ? argv.map((q) => ({ label: "argv", question: q }))
  : [{ label: "default", question: demoQuestion }]
      .concat(chips.map((q) => ({ label: "chip", question: q })));

const out = {
  app_js: APP_JS,
  index_html: INDEX_HTML,
  lexicon_size: mod.lexicon.length,
  max_terms: mod.maxTerms,
  cases: cases.map((c) => {
    const r = mod.rewrite(c.question);
    return {
      label: c.label,
      question: c.question,
      rewritten: r.rewritten,
      search_terms: r.terms,
    };
  }),
};
// Determinism check: run every case 5x and require byte-identical output.
const again = cases.map((c) => JSON.stringify(mod.rewrite(c.question)));
for (let k = 0; k < 4; k++) {
  const now = cases.map((c) => JSON.stringify(mod.rewrite(c.question)));
  if (JSON.stringify(now) !== JSON.stringify(again)) {
    out.determinism = "FAIL: rewrite output differed across runs";
    console.log(JSON.stringify(out, null, 2));
    process.exit(1);
  }
}
out.determinism = "PASS: 5/5 runs identical for every case";
console.log(JSON.stringify(out, null, 2));
