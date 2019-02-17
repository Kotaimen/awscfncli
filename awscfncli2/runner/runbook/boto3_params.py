import os
from collections import OrderedDict

import six

from awscfncli2.config import CANNED_STACK_POLICIES, ConfigError


def normalize_value(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    elif isinstance(v, int):
        return str(v)
    else:
        return v


def make_boto3_parameters(parameters, is_packaging):
    # inject parameters
    StackName = parameters['StackName']

    Template = parameters['Template']
    if Template is None:
        raise ConfigError('No template found, specify Template as a local file or S3 url.')
    elif Template.startswith('https') or Template.startswith('http'):
        # s3 template
        TemplateURL, TemplateBody = Template, None
    elif is_packaging:
        # local template with package=on
        TemplateURL = Template
        TemplateBody = None
    else:
        # local template
        TemplateURL = None
        with open(Template) as fp:
            TemplateBody = fp.read()

    # lookup canned policy
    StackPolicy = parameters['StackPolicy']
    if StackPolicy is not None:
        try:
            StackPolicyBody = CANNED_STACK_POLICIES[StackPolicy]
        except KeyError:
            # treat as local file
            if os.path.exists(StackPolicy) and os.path.isfile(StackPolicy):
                try:
                    with open(StackPolicy) as fp:
                        StackPolicyBody = fp.read()
                except Exception as ex:
                    raise ConfigError(
                        'Error reading stack policy {}'.format(StackPolicy))
            else:
                raise ConfigError(
                    'Invalid stack policy, either specify a canned policy name '
                    'or a local policy document.')
    else:
        StackPolicyBody = None
    StackPolicyURL = None

    # Normalize parameter config
    Parameters = parameters['Parameters']
    normalized_params = None
    if Parameters and isinstance(Parameters, dict):
        normalized_params = list(
            {
                'ParameterKey': k,
                'ParameterValue': normalize_value(v)
            }
            for k, v in
            six.iteritems(OrderedDict(
                sorted(six.iteritems(Parameters)))
            )
        )

    # Normalize tag config
    Tags = parameters['Tags']
    normalized_tags = None
    if Tags and isinstance(Tags, dict):
        normalized_tags = list(
            {'Key': k, 'Value': v}
            for k, v in
            six.iteritems(OrderedDict(
                sorted(six.iteritems(Tags)))
            )
        )

    normalized_config = dict(
        StackName=StackName,
        TemplateURL=TemplateURL,
        TemplateBody=TemplateBody,
        DisableRollback=parameters['DisableRollback'],
        RollbackConfiguration=parameters['RollbackConfiguration'],
        TimeoutInMinutes=parameters['TimeoutInMinutes'],
        NotificationARNs=parameters['NotificationARNs'],
        Capabilities=parameters['Capabilities'],
        ResourceTypes=parameters['ResourceTypes'],
        RoleARN=parameters['RoleARN'],
        OnFailure=parameters['OnFailure'],
        StackPolicyBody=StackPolicyBody,
        StackPolicyURL=StackPolicyURL,
        Parameters=normalized_params,
        Tags=normalized_tags,
        EnableTerminationProtection=parameters['EnableTerminationProtection'],
    )

    # drop all None and empty list
    return dict(
        (k, v) for k, v in six.iteritems(normalized_config) if
        v is not None)
