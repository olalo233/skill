# Back-of-the-envelope reference points

Condensed from vendor/system-design/skills/back-of-the-envelope
(proyecto26/system-design-skills, MIT). Memorize orders of magnitude, not
decimals — the ratios between components are what shift an architecture.

## Powers and time

- Storage/memory are base-2 (2^10≈1K, 2^20≈1M, 2^30≈1G, 2^40≈1T, 2^50≈1P);
  marketing disk/network sizes are base-10.
- Seconds in a day ≈ 86,400 ≈ 10^5 — divide per-day volumes by ~100,000 to get
  per-second rates.

## Latency orders of magnitude

| Operation | ≈ Time |
|---|---:|
| Main memory reference | ~100 ns |
| Read 1 MB sequentially from memory | ~3–10 µs |
| SSD random read | ~16 µs |
| Read 1 MB sequentially from SSD | ~50–200 µs |
| Round trip within a datacenter | ~500 µs |
| Disk seek | ~2–10 ms |
| Read 1 MB sequentially from disk | ~1–30 ms |
| Cross-continent network round trip | ~70–150 ms |

Takeaways: memory is fast, disk is slow; avoid seeks; a cross-continent hop
costs as much as hundreds of disk reads; compression buys bandwidth at CPU cost.

## Quick estimation moves

- **QPS**: daily active users × requests-per-user-per-day ÷ 10^5; peak ≈ 2–3×
  average unless the product says otherwise (live events: much higher).
- **Storage**: writes/sec × record size × retention seconds; then add index and
  replication overhead (×2–3 is a sane first cut).
- **Bandwidth**: QPS × response size; separate read and write paths.
- **Cache sizing**: cache only what the 80/20 says is hot; a small fraction of
  working set usually absorbs most reads.
- State assumptions next to every number — the estimate exists to be argued
  with, and a wrong assumption should change the design, not hide.
