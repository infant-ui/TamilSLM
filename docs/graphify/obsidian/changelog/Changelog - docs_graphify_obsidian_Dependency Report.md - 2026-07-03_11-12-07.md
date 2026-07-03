# Changelog: docs/graphify/obsidian/Dependency Report.md
**Date:** 2026-07-03_11-12-07
**Type:** Modified

## Summary of Changes
### Structural Changes Detected (Best-Effort)
- None detected

## Diff
```diff
diff --git a/docs/graphify/obsidian/Dependency Report.md b/docs/graphify/obsidian/Dependency Report.md
index 20e9b73..10e8a99 100644
--- a/docs/graphify/obsidian/Dependency Report.md	
+++ b/docs/graphify/obsidian/Dependency Report.md	
@@ -1,237 +1,259 @@
 # Dependency Report
 
 ## Libraries
-- idna=3.4=pypi_0
+- jiwer=3.0.2=pypi_0
+- xformers=0.0.22.post4=pypi_0
+- requests
+- parso=0.8.3=pyhd8ed1ab_0
+- nvidia-cuda-nvrtc-cu12=12.1.105=pypi_0
+- nvidia-cuda-runtime-cu12=12.1.105=pypi_0
+- async-timeout=4.0.3=pypi_0
+- cmaes=0.10.0=pypi_0
+- nvidia-curand-cu12=10.3.2.106=pypi_0
+- trl=0.4.7=pypi_0
+- gradio-client=0.5.0=pypi_0
+- jedi=0.19.1=pyhd8ed1ab_0
+- joblib=1.3.1=pypi_0
+- pillow=10.0.0=pypi_0
+- psutil=5.9.6=pypi_0
+- python=3.10.13=h955ad1f_0
+- pytz=2023.3.post1=pypi_0
+- certifi=2023.7.22=pypi_0
+- six=1.16.0=pyh6c4a22f_0
+- codecarbon=2.2.3=pypi_0
+- gradio=3.41.0=pypi_0
+- zeromq=4.3.4=h2531618_0
+- starlette=0.27.0=pypi_0
+- tiktoken=0.5.1=pypi_0
+- prompt_toolkit=3.0.39=hd8ed1ab_0
+- tzdata=2023.3=pypi_0
+- tensorboard-data-server=0.7.1=pypi_0
+- httpx=0.25.0=pypi_0
+- contourpy=1.1.1=pypi_0
+- scikit-learn=1.3.0=pypi_0
+- opencv-python-headless=4.8.1.78=pypi_0
+- tyro=0.5.10=pypi_0
 - typing-extensions=4.8.0=hd8ed1ab_0
-- sympy=1.12=pypi_0
-- sentencepiece=0.1.99=pypi_0
-- mako=1.2.4=pypi_0
-- backcall=0.2.0=pyh9f0ad1d_0
-- loguru=0.7.0=pypi_0
-- rpds-py=0.10.6=pypi_0
-- zlib=1.2.13=h5eee18b_0
-- py-cpuinfo=9.0.0=pypi_0
+- typing_extensions=4.8.0=pyha770c72_0
 - xz=5.4.2=h5eee18b_0
-- fastapi>=0.100.0
-- exceptiongroup=1.1.3=pyhd8ed1ab_0
-- regex=2023.10.3=pypi_0
-- traitlets=5.12.0=pypi_0
-- jedi=0.19.1=pyhd8ed1ab_0
+- importlib-resources=6.1.0=pypi_0
+- responses=0.18.0=pypi_0
+- yarl=1.9.2=pypi_0
+- requests=2.31.0=pypi_0
+- libgomp=11.2.0=h1234567_1
+- sqlite=3.41.2=h5eee18b_0
 - deep-translator
-- arrow=1.3.0=pypi_0
-- readline=8.2=h5eee18b_0
-- pydub=0.25.1=pypi_0
-- stack_data=0.6.2=pyhd8ed1ab_0
-- tokenizers=0.13.3=pypi_0
-- entrypoints=0.4=pyhd8ed1ab_0
-- wheel=0.41.2=py310h06a4308_0
-- jsonschema=4.19.1=pypi_0
+- asttokens=2.4.1=pyhd8ed1ab_0
+- ipadic=1.0.0=pypi_0
+- gradio
 - ptyprocess=0.7.0=pyhd3deb0d_0
-- dill=0.3.7=pypi_0
-- qudida=0.0.4=pypi_0
-- pyasn1=0.5.0=pypi_0
-- python_abi=3.10=2_cp310
-- typing_extensions=4.8.0=pyha770c72_0
-- datasets=2.14.5=pypi_0
-- albumentations=1.3.1=pypi_0
-- opencv-python-headless=4.8.1.78=pypi_0
-- pfzy=0.3.4=pypi_0
+- readline=8.2=h5eee18b_0
+- autotrain-advanced=0.6.37=pypi_0
+- xxhash=3.4.1=pypi_0
+- httpcore=0.18.0=pypi_0
+- _libgcc_mutex=0.1=main
+- python-multipart=0.0.6=pypi_0
+- backports.functools_lru_cache=1.6.5=pyhd8ed1ab_0
+- ipykernel=6.26.0=pyhf8b6a83_0
+- bzip2=1.0.8=h7b6447c_0
+- opencv-python=4.8.1.78=pypi_0
+- pyarrow=13.0.0=pypi_0
+- click=8.1.7=pypi_0
+- aiosignal=1.3.1=pypi_0
+- toolz=0.12.0=pypi_0
+- cycler=0.12.1=pypi_0
+- rsa=4.9=pypi_0
+- aiofiles=23.2.1=pypi_0
+- langdetect
+- pydantic=1.10.11=pypi_0
+- executing=2.0.1=pyhd8ed1ab_0
+- idna=3.4=pypi_0
+- multiprocess=0.70.15=pypi_0
+- sentence-transformers
+- pyzmq=25.1.0=py310h6a678d5_0
+- openssl=3.0.11=h7f8727e_2
+- jsonschema-specifications=2023.7.1=pypi_0
+- nvidia-nvtx-cu12=12.1.105=pypi_0
 - wcwidth=0.2.8=pypi_0
-- prompt_toolkit=3.0.39=hd8ed1ab_0
-- jinja2=3.1.2=pypi_0
-- ipadic=1.0.0=pypi_0
-- pyparsing=3.1.1=pypi_0
-- markdown-it-py=3.0.0=pypi_0
-- accelerate=0.21.0=pypi_0
+- kiwisolver=1.4.5=pypi_0
+- nvidia-cusparse-cu12=12.1.0.106=pypi_0
+- pygments=2.16.1=pyhd8ed1ab_0
+- optuna=3.3.0=pypi_0
+- websockets=11.0.3=pypi_0
+- fastapi
+- scipy=1.11.3=pypi_0
+- python_abi=3.10=2_cp310
+- tensorboard=2.15.0=pypi_0
+- ffmpy=0.3.1=pypi_0
+- dill=0.3.7=pypi_0
+- fastapi=0.104.0=pypi_0
+- invisible-watermark=0.2.0=pypi_0
+- mako=1.2.4=pypi_0
+- regex=2023.10.3=pypi_0
+- tk=8.6.12=h1ccaba5_0
+- loguru=0.7.0=pypi_0
+- sentencepiece=0.1.99=pypi_0
+- jsonschema=4.19.1=pypi_0
+- absl-py=2.0.0=pypi_0
 - fonttools=4.43.1=pypi_0
+- arrow=1.3.0=pypi_0
+- faiss-cpu
+- tifffile=2023.9.26=pypi_0
+- werkzeug=2.3.6=pypi_0
+- python-dateutil=2.8.2=pyhd8ed1ab_0
+- importlib-metadata=6.8.0=pypi_0
+- markupsafe=2.1.3=pypi_0
 - safetensors=0.4.0=pypi_0
-- toolz=0.12.0=pypi_0
+- py-cpuinfo=9.0.0=pypi_0
+- tornado=6.1=py310h5764c6d_3
 - backports=1.0=pyhd8ed1ab_3
-- charset-normalizer=3.3.0=pypi_0
-- matplotlib-inline=0.1.6=pyhd8ed1ab_0
+- packaging=23.1=pypi_0
+- triton=2.1.0=pypi_0
+- anyio=3.7.1=pypi_0
+- fuzzywuzzy=0.18.0=pypi_0
+- tokenizers=0.13.3=pypi_0
+- nvidia-cusolver-cu12=11.4.5.107=pypi_0
+- _openmp_mutex=5.1=1_gnu
+- attrs=23.1.0=pypi_0
+- zipp=3.17.0=pypi_0
+- markdown-it-py=3.0.0=pypi_0
+- backcall=0.2.0=pyh9f0ad1d_0
+- bitsandbytes=0.40.2=pypi_0
+- jupyter_client=7.3.4=pyhd8ed1ab_0
+- xgboost=1.7.6=pypi_0
+- flash-attn=2.3.3=pypi_0
+- libffi=3.4.4=h6a678d5_0
 - colorlog=6.7.0=pypi_0
-- pure_eval=0.2.2=pyhd8ed1ab_0
-- libstdcxx-ng=11.2.0=h1234567_1
-- rich=13.6.0=pypi_0
-- aiohttp=3.8.6=pypi_0
-- scipy=1.11.3=pypi_0
-- nvidia-cuda-nvrtc-cu12=12.1.105=pypi_0
+- libsodium=1  # Truncated to 5000 chars for readability if huge
```

## Related Links
- [[Docs]]
- [[Home]]
- [[Changelog Index]]
