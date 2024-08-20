ARG PYTHON_VERSION=
ARG ROOT_DIR=
FROM public.ecr.aws/sam/build-python${PYTHON_VERSION}

RUN pip install --upgrade pip && \
    mkdir /usr/extras && \
    touch /usr/extras/__extra__


# Compatible with initial base image
ENTRYPOINT []
CMD ["/bin/bash"]
