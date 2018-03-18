# -*- coding: utf-8 -*-

import os
import yaml
import click

from awscli.customizations.cloudformation.artifact_exporter import Template, \
    EXPORT_DICT

try:
    from awscli.customizations.cloudformation.s3uploader import S3Uploader
except ImportError:
    # Fix import error for awscli version later than 1.11.161
    from awscli.customizations.s3uploader import S3Uploader

from ...config import ConfigError


def package_template(session, template_path, bucket_region,
                     bucket_name=None, prefix=None, kms_key_id=None):
    # validate template path
    if not os.path.isfile(template_path):
        raise ConfigError('Invalid Template Path "%s"' % template_path)

    # if bucket name is not provided, create a defualt bucket with name
    # awscfncli-{AWS::AccountId}-{AWS::Region}
    if bucket_name is None:
        sts = session.client('sts')
        account_id = sts.get_caller_identity()["Account"]
        bucket_name = 'awscfncli-%s-%s' % (account_id, bucket_region)

    s3_client = session.create_client('s3')
    s3_uploader = S3Uploader(
        s3_client,
        bucket_name,
        bucket_region,
        prefix,
        kms_key_id,
        force_upload=False
    )

    template = Template(template_path, os.getcwd(), s3_uploader,
                        resources_to_export=EXPORT_DICT)
    exported_template = template.export()
    exported_str = yaml.safe_dump(exported_template)

    click.echo("Successfully packaged artifacts and "
               "uploaded file {template_path} to {bucket_name}".format(
        template_path=template_path, bucket_name=bucket_name))

    return exported_str
