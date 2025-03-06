.PHONY: run--ui

run--ui: ## Run the CPM test UI on localhost
	npm run --prefix test_ui/product_id_flow dev
