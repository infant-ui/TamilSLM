# Scripts

One-off and maintenance scripts moved out of the repo root. None are imported by the backend or frontend.

- `ingestion_experiments/`: OCR / PyMuPDF / chunking experiments. They read and write files relative to the current directory, so run them from the folder that holds their inputs (the sample page PNGs used by `paddle_preflight.py` were deleted from the root; recover them from git history if needed).
- `ops/`: GPU-server and housekeeping helpers. `connect_gpu_server.py` reads credentials from `.env` (`GPU_SERVER_HOST`, `GPU_SERVER_USER`, `GPU_SERVER_PASSWORD`).
- `data/`: glossary extraction, content inventory and report generation. Outputs are written to the current directory; the committed copies live in `data/derived/`.
- `docs/`: documentation regeneration (`generate_docs.bat`, run from anywhere; it changes into the repo root itself).
