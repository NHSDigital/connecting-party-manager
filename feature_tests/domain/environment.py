from behave.model import Feature, Scenario

from feature_tests.domain.steps.context import Context
from feature_tests.feature_test_helpers import TestMode


def before_feature(context: Context, feature: Feature):
    # At present we only run domain tests in 'local' mode
    test_mode = TestMode.parse(config=context.config)
    if test_mode is not TestMode.LOCAL:
        feature.mark_skipped()


def before_scenario(context: Context, scenario: Scenario):
    context.questionnaires = {}
    context.ods_organisations = {}
    context.events = []
    context.error = None
    context.result = None
    context.subject = None
