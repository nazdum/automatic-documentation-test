#!/usr/bin/env python3
"""Definition for cdk for beta puntogroumet.co beta stack."""
import os

import aws_cdk as cdk

from s3_website.s3_website_stack import S3WebsiteStack


app = cdk.App()
"""This the CDK application entry point, it gets run during cdk deploy."""

website = app.node.try_get_context("website")
domain_name = ''
sub_domain_name = ''

parts = website.split(".")
if len(parts) == 2:
    domain_name = website
else:   
    sub_domain_name = ".".join(parts[:-2])
    domain_name = ".".join(parts[-2:])


props = {
#    "namespace": app.node.try_get_context("namespace"),
    "domain_name": domain_name,
    "sub_domain_name": sub_domain_name,
    "domain_certificate_arn": app.node.try_get_context("domain_certificate_arn")    
}
"""properties for the stack we are creating"""

env = cdk.Environment(
    account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ.get("CDK_DEFAULT_ACCOUNT")),
    region=os.environ.get("CDK_DEPLOY_REGION", os.environ.get("CDK_DEFAULT_REGION")),
)



S3WebsiteStack(
    scope=app,
    construct_id=website.replace('.','-'),
    env=env,
    props=props,
    description="Static S3 Site served as a CloudFront Distribution",
)



app.synth()
"""This is the entrypoint for cdk deploy and cdk synth for creating the stack."""
