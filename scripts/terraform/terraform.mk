.PHONY: terraform--plan terraform--apply terraform--destroy

# UNCOMMENT THIS AFTER RUNNERS INSTALLED
# terraform--plan: build aws--login  ## Run terraform plan
#	@echo "terraform--plan" $(CI) $(WORKSPACE) $(AWS_ACCESS_KEY_ID) $(AWS_SECRET_ACCESS_KEY) $(AWS_DEFAULT_REGION)

# DELETE THIS AFTER RUNNERS INSTALLED
terraform--init: aws--login  ## Run terraform init
	@echo "terraform--init" $(CI) $(WORKSPACE) $(AWS_ACCESS_KEY_ID) $(AWS_SECRET_ACCESS_KEY) $(AWS_DEFAULT_REGION)

terraform--plan: aws--login  ## Run terraform plan
	@echo "terraform--plan" $(CI) $(WORKSPACE) $(AWS_ACCESS_KEY_ID) $(AWS_SECRET_ACCESS_KEY) $(AWS_DEFAULT_REGION)

terraform--apply: terraform--plan  ## Run terraform apply
	@echo "terraform--apply" $(CI) $(WORKSPACE) $(AWS_ACCESS_KEY_ID) $(AWS_SECRET_ACCESS_KEY) $(AWS_DEFAULT_REGION)

terraform--destroy: terraform--plan  ## Run terraform destroy
	@echo "terraform--destroy" $(CI) $(WORKSPACE) $(AWS_ACCESS_KEY_ID) $(AWS_SECRET_ACCESS_KEY) $(AWS_DEFAULT_REGION)
