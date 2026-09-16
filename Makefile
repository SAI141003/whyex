install:
	pip install -e .

test:
	python3 -m pytest -q

lint:
	python3 -m pyflakes why.py rules.py tests || true

build:
	python3 -m build

binary:
	@python3 -c "import PyInstaller" 2>/dev/null || pip install pyinstaller
	pyinstaller whyex.spec

clean:
	rm -rf build dist *.egg-info __pycache__ .pytest_cache
