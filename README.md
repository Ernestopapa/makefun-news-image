# News Image Generator

This program generates a newsroom front-page grid for Friday, 13 November 2026. It draws a header banner with the date and six illustrated tiles, each representing a key news story with a short bold label.

## Specification
- Canvas: 1024x1024 pixel PNG (RGB, no alpha).
- Output: The program writes to `<output_dir>/entry.png`. The output directory can be set via the `MAKEFUN_OUTPUT_DIR` environment variable, which defaults to `/output` if not provided.
- Deterministic: The image generation process is deterministic. Running the program multiple times with the same input parameters will produce byte-identical PNG files.
- Implementation: Written in Python 3.13 using only the standard library (math, struct, zlib, os).

## Stories
- NVIDIA CEO: `NVIDIA CEO` / `HUANG RESIGNS`
- UKRAINE TALKS: `UKRAINE TALKS` / `EUROPE JOINS`
- IRAN CLAIMS: `IRAN CLAIMS` / `RADAR STRIKE`
- FBI: N. KOREA: `FBI: N. KOREA` / `STEALS $400M`
- GAZA: `STRIKE ON` / `GAZA HOSPITAL` / `KILLS 6`
- KANE: `KANE SETS` / `ENGLAND CAPS` / `RECORD: 126`

## Running the program
```bash
export MAKEFUN_OUTPUT_DIR=/path/to/output
python3 main.py
```
This will create `entry.png` in the specified directory.
