.PHONY: help install test lint format clean docker-build docker-run gui cli

help:
	@echo "Comandos disponíveis:"
	@echo "  make install      - Instala dependências"
	@echo "  make test         - Executa testes"
	@echo "  make lint         - Executa linting"
	@echo "  make format       - Formata código"
	@echo "  make clean        - Limpa arquivos temporários"
	@echo "  make gui          - Inicia interface gráfica"
	@echo "  make cli          - Inicia CLI interativo"
	@echo "  make docker-build - Build da imagem Docker"
	@echo "  make docker-run   - Executa container Docker"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/ --line-length 100
	isort src/ tests/

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache htmlcov
	rm -rf *.egg-info dist build
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

gui:
	python -m src.gui

cli:
	python -m src.cli interactive

docker-build:
	docker build -f docker/Dockerfile -t conversor-moedas .

docker-run:
	docker run -it --rm conversor-moedas

docker-gui:
	docker run -it --rm \
		-e DISPLAY=$$DISPLAY \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		conversor-moedas python -m src.gui
