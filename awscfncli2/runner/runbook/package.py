# -*- coding: utf-8 -*-

import logging
import os
import tempfile

from awscli.customizations.cloudformation import exceptions
from awscli.customizations.cloudformation.artifact_exporter import Template, \
    Resource, make_abs_path
from awscli.customizations.s3uploader import S3Uploader
from awscli.customizations.cloudformation.yamlhelper import yaml_dump
from botocore.exceptions import ClientError

# Before 1.11.16, unsupported now
# from awscli.customizations.cloudformation.s3uploader import S3Uploader

try:

    from awscli.customizations.cloudformation.artifact_exporter import \
        RESOURCES_EXPORT_LIST as EXPORTS
except ImportError:
    try:
        # for awscli < 1.16.77
        from awscli.customizations.cloudformation.artifact_exporter import \
            EXPORT_LIST as EXPORTS
    except ImportError:
        # for awscli < 1.16.23
        from awscli.customizations.cloudformation.artifact_exporter import \
            EXPORT_DICT as EXPORTS

from ...config import ConfigError

TEMPLATE_BODY_SIZE_LIMIT = 51200


def generate_tempfile():
    return os.path.join(tempfile.gettempdir(), os.urandom(24).hex())


def package_template(ppt, session, template_path, bucket_region,
                     bucket_name=None, prefix=None, kms_key_id=None):
    # validate template path
    if not os.path.isfile(template_path):
        raise ConfigError('Invalid Template Path "%s"' % template_path)

    # if bucket name is not provided, create a default bucket with name
    # awscfncli-{AWS::AccountId}-{AWS::Region}
    if bucket_name is None:
        sts = session.client('sts')
        account_id = sts.get_caller_identity()["Account"]
        bucket_name = 'awscfncli-%s-%s' % (account_id, bucket_region)
        ppt.secho('Using default artifact bucket s3://{}'.format(bucket_name))
    else:
        ppt.secho('Using specified artifact bucket s3://{}'.format(bucket_name))

    s3_client = session.client('s3')

    # create bucket if not exists
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            if bucket_region != 'us-east-1':
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': bucket_region
                    }
                )
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name
                )
            ppt.secho('Created artifact bucket {}'.format(bucket_name))
        else:
            raise e

    try:
        s3_uploader = S3Uploader(
            s3_client,
            bucket_name,
            bucket_region,
            prefix,
            kms_key_id,
            force_upload=False
        )
    except TypeError:
        # HACK: since awscli 1.16.145+ the bucket region parameter is removed
        s3_uploader = S3Uploader(
            s3_client,
            bucket_name,
            prefix,
            kms_key_id,
            force_upload=False
        )

    template = Template(template_path, os.getcwd(), s3_uploader,
                        resources_to_export=EXPORTS)

    exported_template = template.export()

    ppt.secho('Successfully packaged artifacts and '
              'uploaded to s3://{bucket_name}.'.format(bucket_name=bucket_name),
              fg='green')

    template_body = yaml_dump(exported_template)

    template_data = template_body.encode('ascii')
    if len(template_data) <= TEMPLATE_BODY_SIZE_LIMIT:
        template_url = None
    else:
        ppt.secho('Template body is too large, uploading as artifact.',
                  fg='red')

        tempfile_path = generate_tempfile()
        with open(tempfile_path, 'wb') as fp:
            # write template body to local temp file
            fp.write(template_data)
            fp.flush()
            # upload to s3
            template_location = s3_uploader.upload_with_dedup(
                fp.name,
                extension='template.json')
            ppt.secho('Template uploaded to %s' % template_location)

        # get s3 object key ...upload_with_dedup() returns s3://bucket/key
        template_key = template_location.replace('s3://%s/' % bucket_name, '')
        # generate a pre-signed url for CloudFormation as the object in S3
        # is private by default
        template_url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket_name, 'Key': template_key},
            ExpiresIn=3600
        )

    return template_body, template_url


# XXX: Hack, Register customized Resource in AWS Cli
class ResourceWithInlineCode(Resource):
    def __init__(self, uploader):
        super(ResourceWithInlineCode, self).__init__(None)

    def export(self, resource_id, resource_dict, parent_dir):
        if resource_dict is None:
            return

        property_value = resource_dict.get(self.PROPERTY_NAME, None)

        if not property_value and not self.PACKAGE_NULL_PROPERTY:
            return

        if isinstance(property_value, dict):
            logging.debug("Property {0} of {1} resource is not a file path"
                          .format(self.PROPERTY_NAME, resource_id))
            return

        try:
            self.do_export(resource_id, resource_dict, parent_dir)

        except Exception as ex:
            logging.debug("Unable to export", exc_info=ex)
            raise exceptions.ExportFailedError(
                resource_id=resource_id,
                property_name=self.PROPERTY_NAME,
                property_value=property_value,
                ex=ex)

    def do_export(self, resource_id, resource_dict, parent_dir):
        """
        Upload to S3 and set property to an dict representing the S3 url
        of the uploaded object
        """

        local_path = resource_dict.get(self.PROPERTY_NAME, None)
        local_path = make_abs_path(parent_dir, local_path)

        with open(local_path, 'r') as fp:
            data = fp.read()

        resource_dict[self.PROPERTY_NAME] = data


class KinesisAnalysisApplicationCode(ResourceWithInlineCode):
    RESOURCE_TYPE = 'AWS::KinesisAnalytics::Application'
    PROPERTY_NAME = 'ApplicationCode'


class StepFunctionsDefinitionString(ResourceWithInlineCode):
    RESOURCE_TYPE = 'AWS::StepFunctions::StateMachine'
    PROPERTY_NAME = 'DefinitionString'


ADDITIONAL_EXPORT = {
    # KinesisAnalysisApplicationCode.RESOURCE_TYPE: KinesisAnalysisApplicationCode,
    # StepFunctionsDefinitionString.RESOURCE_TYPE: StepFunctionsDefinitionString
}

if isinstance(EXPORTS, dict):
    EXPORTS.update(ADDITIONAL_EXPORT)
elif isinstance(EXPORTS, list):
    EXPORTS.extend(ADDITIONAL_EXPORT.values())
