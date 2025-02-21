resource "local_file" "rendered_swagger" {
  content  = sensitive(local.swagger_file)
  filename = "${path.root}/../../swagger/dist/aws/rendered/swagger.yaml"
}
