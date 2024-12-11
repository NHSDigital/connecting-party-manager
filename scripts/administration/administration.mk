SET_GENERATOR_COUNT :=

admin--generate-ids--product: ## Generate product Ids
	poetry run python scripts/administration/id_generator.py --count="$(SET_GENERATOR_COUNT)"
