# Single agent with tool call

Single agent that can use 3 tools. The agent are using a local LLM running using ollama.
To run the project:


## Getting started

To locally run the [llama3.1](https://ollama.com/library/llama3.1:8b), we are using [text](https://ollama.com/download/linux) version 0.5.7

Pull llama3.1:8b
```
ollama pull llama3.1:8b
```

The project uses [uv](https://docs.astral.sh/uv/) version 0.6.5 as a dependency management tool.

Create a development environment:
```
uv sync
```

Run the project:
```
uv run main.py
```