from feature_tests.steps.context import Context

# def before_all(context):
#     pass


# def after_all(context):
#     pass

# def before_feature(context, feature):
#     pass

# def after_feature(context, feature):
#     pass


def before_scenario(context: Context, scenario):
    context.questionnaires = {}
    context.users = {}
    context.ods_organisations = {}
    context.events = []
    context.error = None
    context.result = None
    context.subject = None


# def after_scenario(context, scenario):
#     pass

# def before_tags(context, tag):
#     pass

# def after_tags(context, tag):
#     pass

# def before_step(context, step):
#     pass

# def after_step(context, step):
#     pass
