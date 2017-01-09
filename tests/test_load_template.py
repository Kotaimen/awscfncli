# -*- encoding: utf-8 -*-

import json
import pytest
from botocore.stub import Stubber

from awscfncli.cli import load_template, _s3_client

__author__ = 'ray'
__date__ = '1/5/17'

MOCK_TEMPLATE = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Resources": {
        "S3Bucket": {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "AccessControl": "PublicRead",
                "WebsiteConfiguration": {
                    "IndexDocument": "index.html",
                    "ErrorDocument": "error.html"
                }
            },
            "DeletionPolicy": "Retain"
        }
    },
    "Outputs": {
        "WebsiteURL": {
            "Value": {"Fn::GetAtt": ["S3Bucket", "WebsiteURL"]},
            "Description": "URL for website hosted on S3"
        },
        "S3BucketSecureURL": {
            "Value": {"Fn::Join": ["", ["https://", {
                "Fn::GetAtt": ["S3Bucket", "DomainName"]}]]},
            "Description": "Name of S3 bucket to hold website content"
        }
    }
}

_stabber = Stubber(_s3_client)


def start_mock_s3():
    expected_response = {
        "Body": json.dumps(MOCK_TEMPLATE)
    }

    expected_params = {
        "Bucket": "test-bucket",
        "Key": "test.template"
    }

    _stabber.add_response('get_object', expected_response, expected_params)
    _stabber.activate()


def stop_mock_s3():
    _stabber.deactivate()


@pytest.fixture(scope='session')
def template_file(tmpdir_factory):
    path = tmpdir_factory.mktemp('template').join('Bucket.template')
    path.write(json.dumps(MOCK_TEMPLATE))
    yield path
    path.remove()


def test_load_template_from_file(template_file):
    t = json.loads(load_template(template_file.strpath))
    assert t == MOCK_TEMPLATE


# def test_load_template_from_url():
#     t = json.loads(load_template('http://example.com/test.template'))
#     assert t == MOCK_TEMPLATE
#
#     t = json.loads(load_template('https://example.com/test.template'))
#     assert t == MOCK_TEMPLATE
#

def test_load_template_from_s3():
    start_mock_s3()
    t = json.loads(load_template('s3://test-bucket/test.template'))
    assert t == MOCK_TEMPLATE
    stop_mock_s3()
