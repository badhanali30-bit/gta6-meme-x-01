// gta6-meme-x-01 entry program (Node 22, standard library only).
//
// The entry itself is the X post: the meme (meme.png, drawn by draw_meme.py)
// is posted on X from a public account, and POST.json at this repository's
// root names that post. All this program has to do is copy POST.json from
// the repository into /output/POST.json, where the house's gate reads it.
//
// No network, no wall clock, no files outside the repository: the two runs
// of an entry write the same bytes.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const SOURCE = join(BOT_DIR, 'POST.json');
const TARGET = join(OUTPUT_DIR, 'POST.json');

// The gate reads POST.json from /output, so the copy must land exactly
// there; creating the directory first keeps the copy from failing on a
// fresh container.
mkdirSync(OUTPUT_DIR, { recursive: true });

try {
  copyFileSync(SOURCE, TARGET);
} catch (err) {
  console.error(`could not copy ${SOURCE} to ${TARGET}: ${(err as Error).message}`);
  process.exit(1);
}
