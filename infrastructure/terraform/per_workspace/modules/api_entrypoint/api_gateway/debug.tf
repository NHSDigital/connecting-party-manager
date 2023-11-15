resource "local_file" "rendered_swagger" {
  content  = sensitive(data.template_file.swagger.rendered)
  filename = "${path.root}/../../swagger/dist/aws/rendered/swagger.yaml"
}
