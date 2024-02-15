from types import FunctionType

from etl_utils.worker.exception import render_exception
from event.step_chain import StepChain
from nhs_context_logging import log_action

from .model import WorkerActionResponse, WorkerResponse
from .steps import execute_action, save_processed_records, save_unprocessed_records

_log_action_with_result = lambda function: log_action(
    log_args=["data", "cache"], log_result=True
)(function)
_log_action_without_inputs = lambda function: log_action(log_args=[], log_result=False)(
    function
)


def _render_response(
    action_name: str,
    action_chain_response: WorkerActionResponse | Exception,
    save_chain_response: None | Exception,
) -> WorkerResponse:
    # Collect exceptions in the order that they occurred
    exceptions, is_fatal = [], False

    if isinstance(action_chain_response, Exception):
        is_fatal = True
        exceptions.append(action_chain_response)
    elif action_chain_response.exception is not None:
        exceptions.append(action_chain_response.exception)

    if isinstance(save_chain_response, Exception):
        is_fatal = True
        exceptions.append(save_chain_response)

    error_message = (
        render_exception(
            ExceptionGroup("The following errors were encountered", exceptions)
        )
        if exceptions
        else None
    )

    # Determine the counts of un/processed records if no fatal errors occurred
    count_processed_records = None
    count_unprocessed_records = None
    if not is_fatal:
        count_unprocessed_records = len(action_chain_response.unprocessed_records)
        count_processed_records = len(action_chain_response.processed_records)

    # Pack up the summary
    return WorkerResponse(
        stage_name=action_name,
        processed_records=count_processed_records,
        unprocessed_records=count_unprocessed_records,
        error_message=error_message,
    )


def execute_step_chain(
    action: FunctionType,
    s3_client,
    s3_input_path: str,
    s3_output_path: str,
    unprocessed_dumper: FunctionType,
    processed_dumper: FunctionType,
) -> WorkerResponse:
    # Run the main action chain
    action_chain = StepChain(
        step_chain=[execute_action], step_decorators=[_log_action_without_inputs]
    )
    action_chain.run(init=(action, s3_client, s3_input_path, s3_output_path))

    # Save the action chain results if there were no unhandled (fatal) exceptions
    save_chain_response = None
    if isinstance(action_chain.result, WorkerActionResponse):
        save_chain = StepChain(
            step_chain=[save_unprocessed_records, save_processed_records],
            step_decorators=[_log_action_with_result],
        )
        save_chain.run(
            init=(action_chain.result, s3_client, unprocessed_dumper, processed_dumper)
        )
        save_chain_response = save_chain.result

    # Summarise the outcome of action_chain and step_chain
    return _render_response(
        action_name=action.__name__,
        action_chain_response=action_chain.result,
        save_chain_response=save_chain_response,
    )
