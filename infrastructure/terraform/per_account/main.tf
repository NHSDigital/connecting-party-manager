resource "aws_resourcegroups_group" "test" {
  name = "workspace-resource-group"

  resource_query {
    query = <<JSON
{
  "ResourceTypeFilters": [],
  "TagFilters": [
    {
      "Key": "Workspace",
      "Values": ["Test"]
    }
  ]
}
JSON
  }
}
