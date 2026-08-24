.PHONY: install quality benchmark dashboard

install:
	python -m pip install -e '.[dev,aws]'

quality:
	ruff check src scripts tests
	pytest

benchmark:
	python scripts/benchmark_stream.py --count 10000 --output artifacts/benchmark.json

dashboard:
	./scripts/serve_dashboard.sh
