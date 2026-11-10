# Indélébile : les arcanes de la preuve
# Toutes les commandes passent par uv pour figer les versions (uv.lock).

.PHONY: install test cover reproduce reproduce-small clean

install:
	uv sync

test:
	uv run pytest

cover:
	uv run pytest --cov --cov-report=term-missing

# Complété au fil du week-end : données, évaluation, figures, signature des résultats.
reproduce: install cover
	@echo "reproduce : étapes d'évaluation à venir (week-end du 14-15 novembre)"

reproduce-small: install test

clean:
	rm -rf .pytest_cache .coverage htmlcov results/tmp
