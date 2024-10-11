from nhs_context_logging import log_action as _log_action


def log_action(fn):
    return _log_action(log_args=[], log_result=True)(fn)
