# Changelog: docs/graphify/obsidian/Dependency Report.md
**Date:** 2026-07-03_11-07-55
**Type:** Modified

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/docs/graphify/obsidian/Dependency Report.md b/docs/graphify/obsidian/Dependency Report.md
index 20e9b73..8055cef 100644
--- a/docs/graphify/obsidian/Dependency Report.md	
+++ b/docs/graphify/obsidian/Dependency Report.md	
@@ -1,237 +1,257 @@
 # Dependency Report
 
 ## Libraries
-- idna=3.4=pypi_0
+- charset-normalizer=3.3.0=pypi_0
+- mpmath=1.3.0=pypi_0
+- nvidia-cusparse-cu12=12.1.0.106=pypi_0
+- nvidia-curand-cu12=10.3.2.106=pypi_0
+- comm=0.1.4=pyhd8ed1ab_0
+- pynvml=11.5.0=pypi_0
+- sqlite=3.41.2=h5eee18b_0
+- diffusers=0.21.4=pypi_0
+- frozenlist=1.4.0=pypi_0
+- psutil=5.9.6=pypi_0
+- regex=2023.10.3=pypi_0
+- python_abi=3.10=2_cp310
+- ffmpy=0.3.1=pypi_0
+- pyzmq=25.1.0=py310h6a678d5_0
+- scikit-learn=1.3.0=pypi_0
+- websockets=11.0.3=pypi_0
+- requests-oauthlib=1.3.1=pypi_0
+- google-auth=2.23.3=pypi_0
+- uvicorn
+- altair=5.1.2=pypi_0
+- nvidia-cuda-runtime-cu12=12.1.105=pypi_0
+- optuna=3.3.0=pypi_0
+- filelock=3.12.4=pypi_0
+- grpcio=1.59.0=pypi_0
+- nest-asyncio=1.5.8=pyhd8ed1ab_0
+- _openmp_mutex=5.1=1_gnu
 - typing-extensions=4.8.0=hd8ed1ab_0
-- sympy=1.12=pypi_0
-- sentencepiece=0.1.99=pypi_0
+- attrs=23.1.0=pypi_0
+- requests=2.31.0=pypi_0
+- sentence-transformers
+- semantic-version=2.10.0=pypi_0
+- cachetools=5.3.1=pypi_0
+- ncurses=6.4=h6a678d5_0
+- nvidia-cudnn-cu12=8.9.2.26=pypi_0
+- ptyprocess=0.7.0=pyhd3deb0d_0
+- starlette=0.27.0=pypi_0
+- libgcc-ng=11.2.0=h1234567_1
+- yarl=1.9.2=pypi_0
+- ipykernel=6.26.0=pyhf8b6a83_0
+- tzdata=2023.3=pypi_0
+- pydantic
+- codecarbon=2.2.3=pypi_0
+- safetensors=0.4.0=pypi_0
+- fuzzywuzzy=0.18.0=pypi_0
+- markdown-it-py=3.0.0=pypi_0
+- matplotlib-inline=0.1.6=pyhd8ed1ab_0
+- jupyter_client=7.3.4=pyhd8ed1ab_0
+- jiwer=3.0.2=pypi_0
+- nvidia-nccl-cu12=2.18.1=pypi_0
+- platformdirs=3.11.0=pyhd8ed1ab_0
+- httpx=0.25.0=pypi_0
+- einops=0.6.1=pypi_0
+- Pillow
+- libsodium=1.0.18=h36c2ea0_1
+- packaging=23.1=pypi_0
+- stack-data=0.6.3=pypi_0
+- zeromq=4.3.4=h2531618_0
+- huggingface-hub=0.17.3=pypi_0
 - mako=1.2.4=pypi_0
-- backcall=0.2.0=pyh9f0ad1d_0
-- loguru=0.7.0=pypi_0
-- rpds-py=0.10.6=pypi_0
-- zlib=1.2.13=h5eee18b_0
-- py-cpuinfo=9.0.0=pypi_0
-- xz=5.4.2=h5eee18b_0
-- fastapi>=0.100.0
-- exceptiongroup=1.1.3=pyhd8ed1ab_0
-- regex=2023.10.3=pypi_0
-- traitlets=5.12.0=pypi_0
-- jedi=0.19.1=pyhd8ed1ab_0
-- deep-translator
-- arrow=1.3.0=pypi_0
-- readline=8.2=h5eee18b_0
-- pydub=0.25.1=pypi_0
-- stack_data=0.6.2=pyhd8ed1ab_0
+- transformers=4.31.0=pypi_0
+- alembic=1.12.0=pypi_0
+- setuptools=68.0.0=py310h06a4308_0
 - tokenizers=0.13.3=pypi_0
-- entrypoints=0.4=pyhd8ed1ab_0
-- wheel=0.41.2=py310h06a4308_0
-- jsonschema=4.19.1=pypi_0
-- ptyprocess=0.7.0=pyhd3deb0d_0
 - dill=0.3.7=pypi_0
-- qudida=0.0.4=pypi_0
-- pyasn1=0.5.0=pypi_0
-- python_abi=3.10=2_cp310
-- typing_extensions=4.8.0=pyha770c72_0
-- datasets=2.14.5=pypi_0
-- albumentations=1.3.1=pypi_0
 - opencv-python-headless=4.8.1.78=pypi_0
-- pfzy=0.3.4=pypi_0
-- wcwidth=0.2.8=pypi_0
-- prompt_toolkit=3.0.39=hd8ed1ab_0
-- jinja2=3.1.2=pypi_0
-- ipadic=1.0.0=pypi_0
 - pyparsing=3.1.1=pypi_0
-- markdown-it-py=3.0.0=pypi_0
-- accelerate=0.21.0=pypi_0
-- fonttools=4.43.1=pypi_0
-- safetensors=0.4.0=pypi_0
-- toolz=0.12.0=pypi_0
-- backports=1.0=pyhd8ed1ab_3
-- charset-normalizer=3.3.0=pypi_0
-- matplotlib-inline=0.1.6=pyhd8ed1ab_0
-- colorlog=6.7.0=pypi_0
-- pure_eval=0.2.2=pyhd8ed1ab_0
-- libstdcxx-ng=11.2.0=h1234567_1
+- inquirerpy=0.3.4=pypi_0
+- prompt-toolkit=3.0.39=pyha770c72_0
+- markdown=3.5=pypi_0
+- tiktoken=0.5.1=pypi_0
+- jedi=0.19.1=pyhd8ed1ab_0
+- pfzy=0.3.4=pypi_0
+- pymupdf
+- pydub=0.25.1=pypi_0
+- oauthlib=3.2.2=pypi_0
+- threadpoolctl=3.2.0=pypi_0
 - rich=13.6.0=pypi_0
-- aiohttp=3.8.6=pypi_0
-- scipy=1.11.3=pypi_0
+- idna=3.4=pypi_0
+- executing=2.0.1=pyhd8ed1ab_0
+- pygments=2.16.1=pyhd8ed1ab_0
 - nvidia-cuda-nvrtc-cu12=12.1.105=pypi_0
-- ncurses=6.4=h6a678d5_0
-- autotrain-advanced=0.6.37=pypi_0
-- six=1.16.0=pyh6c4a22f_0
-- huggingface-hub=0.17.3=pypi_0
-- tensorboard=2.15.0=pypi_0
+- cycler=0.12.1=pypi_0
 - xformers=0.0.22.post4=pypi_0
-- yarl=1.9.2=pypi_0
-- pip=23.3=py310h06a4308_0
-- gradio-client=0.5.0=pypi_0
-- lazy-loader=0.3=pypi_0
-- nvidia-cublas-cu12=12.1.3.1=pypi_0
-- inquirerpy=0.3.4=pypi_0
-- httpx=0.25.0=pypi_0
-- ipython=8.16.1=pyh0d859eb_0
-- libuuid=1.41.5=h5eee18b_0
-- debugpy=1.6.7=py310h6a678d5_0
-- sqlalchemy=2.0.22=pypi_0
-- starlette=0.27.0=pypi_0
-- multiprocess=0.70.15=pypi_0
-- protobuf=4.23.4=pypi_0
-- fsspec=2023.6.0=pypi_0
-- anthropic>=0.112.0
-- stack-data=0.6.3=pypi_0
-- optuna=3.3.0=pypi_0
-- networkx=3.2=pypi_0
-- tk=8.6.12=h1ccaba5_0
-- torch=2.1.0=pypi_0
-- nvidia-cuda-cupti-cu12=12.1.105=pypi_0
-- rapidfuzz=2.13.7=pypi_0
-- websockets=11.0.3=pypi_0
+- fastapi=0.104.0=pypi_0
+- jinja2=3.1.2=pypi_0
+- cmaes=0.10.0=pypi_0
 - google-auth-oauthlib=1.1.0=pypi_0
-- scikit-image=0.22.0=pypi_0
-- aiofiles=23.2.1=pypi_0
-- decorator=5.1.1=pyhd8ed1ab_0
-- pyzmq=25.1.0=py310h6a678d5_0
-- sentence-transformers
-- matplotlib=3.8.0=pypi_0
 - md  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Docs]]
- [[Home]]
- [[Changelog Index]]
