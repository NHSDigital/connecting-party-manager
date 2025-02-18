# FHIR, Swagger and generated Pydantic models

We have a "swagger merge" routine to generate our OpenAPI 3 spec for the project. This
spec file is used to underpin our API Gateway (via terraform) as well as acting as public
documentation of the REST API.

It is automatically constructed based initially on swagger models from the open source
[FHIR Swagger Generator tool](https://github.com/LinuxForHealth/FHIR/tree/main/fhir-swagger-generator). You can modify available FHIR endpoints by
editing [our swagger-fhir-generator-definitions/endpoints.yaml](infrastructure/swagger/swagger-fhir-generator-definitions/endpoints.yaml). Updating this file will also
cascade changes to the pydantic models found under the module [domain.fhir.r4](src/layers/domain/fhir/r4), which are used for parsing and validating FHIR objects.

In general, any other additions to be merged on top of the FHIR swagger definition should be
included under [infrastructure/swagger/](infrastructure/swagger/). The enumerated files
(starting with `00_base.yaml`) indicate the order in which the swagger files are merged (note
`00_base.yaml` is actually the base and the FHIR swagger definitions will be merged on top of
this). Therefore if you want to hook up a new endpoint to a e.g. new FHIR definition, then
you should update `05_paths.yaml` and any other relevant files accordingly.

The generated OpenAPI 3 specs, `infrastructure/swagger/dist/aws` and `infrastructure/swagger/ dist/public`, are automatically validated via the node package `redocly-cli`. Any
intermediate merge steps can be viewed under `infrastructure/swagger/build`. Note that
`infrastructure/swagger/dist/aws` is intended for use with API Gateway (and will be rendered
during the `make terraform--apply` into `infrastructure/swagger/dist/aws/rendered`), whilst
`infrastructure/swagger/dist/public` is intended to be used for public facing documentation.

## How to re/generate the Swagger and FHIR Pydantic models

To re/generate the OpenAPI 3 specs and pydantic models after updates to the `swagger-fhir-generator-definitions/config.yaml` or other `infrastructure/swagger` files:

```
make swagger--merge
```

however since this is a dependency of the terraform plan, it is sufficient to run `make terraform--plan` and the OpenAPI 3 specs will be updated accordingly.

## If you have swagger generation issues

If you delete your dist folder when doing work on the swagger you can end up with some odd behaviour, if this is the case then you should do

```
make swagger--clean
```

You should try to do this instead of deleting the dist folder to ensure that everything works correctly
