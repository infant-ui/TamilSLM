@echo off
echo Generating Antigravity Documentation...
python generate_obsidian_kb.py

echo Generating Graphify documentation...
call .venv\Scripts\activate.bat

echo Running graphify for the entire repository (AST only)...
graphify update .

echo Generating Graphify Obsidian vault...
graphify cluster-only . --obsidian --obsidian-dir docs\graphify\obsidian

echo Generating global Callflow HTML...
graphify export callflow-html --output docs\graphify\html\callflow.html

echo Generating modular graphs...
:: If the folders exist, create separate graphs for them to avoid size limits
if exist "backend" (
    graphify extract backend
    graphify export callflow-html backend\graphify-out --output docs\graphify\html\backend_callflow.html
)
if exist "frontend" (
    graphify extract frontend
    graphify export callflow-html frontend\graphify-out --output docs\graphify\html\frontend_callflow.html
)

copy graphify-out\GRAPH_REPORT.md docs\graphify\reports\ 2>nul
copy graphify-out\graph.json docs\graphify\graphs\ 2>nul

echo Documentation generated in docs\graphify\
