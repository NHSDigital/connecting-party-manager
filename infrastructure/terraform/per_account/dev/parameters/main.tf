resource "aws_secretsmanager_secret" "rowans-test-secret-account" {
  name = "${terraform.workspace}-rowans-test-secret-account"
}
