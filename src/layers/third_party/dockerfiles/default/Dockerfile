ARG PYTHON_VERSION=
ARG ROOT_DIR=
FROM public.ecr.aws/sam/build-python${PYTHON_VERSION}

RUN pip install --upgrade pip
RUN mkdir /usr/extras
RUN touch /usr/extras/__extra__

# Compatible with initial base image
ENTRYPOINT []
CMD ["/bin/bash"]
