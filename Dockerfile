FROM public.ecr.aws/lambda/python:3.12

# Copy requirements file and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt


COPY main.py ${LAMBDA_TASK_ROOT}
COPY pretty_print_layout.py ${LAMBDA_TASK_ROOT}

# COPY core ${LAMBDA_TASK_ROOT}/core


CMD ["main.lambda_handler"]
