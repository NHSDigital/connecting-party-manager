.PHONY: terraform--plan terraform--apply terraform--destroy

terraform--plan: build aws--login  ## Run terraform plan
	@echo "terraform--plan"

terraform--apply: terraform--plan  ## Run terraform apply
	@echo "terraform--apply"

terraform--destroy: terraform--plan  ## Run terraform destroy
	@echo "terraform--destroy"
