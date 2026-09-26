=== OEI-012 步骤 4 — 决策证据入口（A5）===
date: 2026-09-26T09:57:07+08:00

完整决策文档: onyx-lab/OEI-012/workspace/retrieval-decision.md

结论（§3.3 三选一）: expansion_off 更优
  - 复现性: expansion_off 1.000 vs expansion_on 0.833 (两两 Jaccard 1.000 vs 0.926)
  - 延迟  : median 1.47s vs 5.02s (3.41x); mean 2.25s vs 10.67s (4.74x)
  - LLM   : expansion_off 36 次里 34 次 <2s; expansion_on 36 次 0 次 <2s
  - 命中率: 两档同为 hit@1=0.0% hit@3=0.0% (无差异)

默认值决定: 保持 skip_query_expansion=False（不翻转，A4）
  数字理由见 retrieval-decision.md §4：翻转买不到命中率改善，且会收窄候选集。

相关证据:
  00-credentials.txt
  00b-baseline.txt
  02-plumbing-diff.txt
  04-retrieval-matrix.json
  04b-run-log.txt
  05-hit-repro-summary.txt
  06-decision.md
