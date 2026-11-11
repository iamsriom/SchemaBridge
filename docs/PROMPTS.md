# Prompts

See prompts/constructor.txt, describer_basic.txt, describer_detailed.txt.
All three are byte-exact and verified on every load by `src/prompt_assets.py`.

| name | file | E1 `prompt_style` | sha256 |
|---|---|---|---|
| basic | `prompts/describer_basic.txt` | `schema2text1` | `e1422bc806119c375d89e44759feee44f13eb2717335154ad3c9ca933b6e6c20` |
| detailed | `prompts/describer_detailed.txt` | `schema2text2` | `f09fc8cae8d8ec73deb79f8bc7c2e71842d5fd35e92d833a02954b539755622d` |
| constructor | `prompts/constructor.txt` | (E2) | `392a396f7073bc015d206460055f7e3b8a3c94a21ed09c059bc47c13d3884ad4` |

User messages:

* basic: `Database name: <db>` + blank line + `DDL:` + DDL.
* detailed: database name, `Number of tables in schema: <n>`, `DDL:` + DDL, and two task lines (one continuous
  English paragraph; no SQL, bullets or headers).
* constructor: `Database name: <db>` + blank line + `Natural language description:` + the E1 description.

The describer prompt files differ from earlier repository revisions; experiments E3-E5 read the same files.
Check: `shasum -a 256 prompts/*.txt`.
