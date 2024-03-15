ARG PYTHON_VERSION=
FROM public.ecr.aws/sam/build-python${PYTHON_VERSION}

RUN yum install -y openldap-devel
RUN pip install --upgrade pip

COPY resolve_dependencies.sh .
COPY resolve_dependencies.py .
RUN mkdir /usr/extras
RUN bash ./resolve_dependencies.sh

# Compatible with initial base image
ENTRYPOINT []
CMD ["/bin/bash"]
