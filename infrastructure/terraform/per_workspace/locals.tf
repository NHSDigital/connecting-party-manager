locals {
  region       = "eu-west-2"
  project      = "nhse-cpm"
  current_time = timestamp()
  # layer_directories = fileset("${path.module}/..", "*")
  # #layer_list        = [for dir in local.layer_directories : dir]
  # layer_list        = split("\n", data.external.directories.result)
  # layer_map         = { for idx, dir in local.layer_list : idx => dir}
}
