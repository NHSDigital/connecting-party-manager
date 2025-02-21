ARG PYTHON_VERSION=
FROM public.ecr.aws/sam/build-python${PYTHON_VERSION}

RUN dnf install -y openldap-devel && pip install --upgrade pip

COPY resolve_dependencies.sh .
COPY resolve_dependencies.py .
RUN mkdir /usr/extras && bash ./resolve_dependencies.sh

# Compatible with initial base image
ENTRYPOINT []
CMD ["/bin/bash"]
