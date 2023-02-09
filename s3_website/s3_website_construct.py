from aws_cdk import RemovalPolicy
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_iam as iam
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as targets
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class S3Website(Construct):
    def __init__(
        self,
        scope,
        construct_id,
        sub_domain_name,
        domain_name,
        website_index_document,
        website_error_document,
        environment,
        domain_certificate_arn=None,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        # Public variables
        self.bucket = None
        self.certificate = None
        self.distribution = None
        self.user = None
        self.group = None
        self.policy = None
        # Internal Variables
        self._site_domain_name = domain_name
        self._site_full_domain_name = f"{domain_name}" if environment == "production" else f"{environment}.{domain_name}"
        self._group_name = domain_name.replace(".", "-") + "-s3-websites-push-group"
        if sub_domain_name:
            self._site_full_domain_name =  f"{sub_domain_name}.{domain_name}" if environment == "production" else f"{environment}.{sub_domain_name}.{domain_name}"
            self._group_name = sub_domain_name.replace(".", "-") + "-" + self._site_domain_name.replace(".", "-") + "-s3-websites-push-group"
        self._website_index_document = website_index_document
        self._website_error_document = website_error_document
        

        # Instance Variables
        self.__domain_certificate_arn = domain_certificate_arn
        self.__hosted_zone_name = domain_name

    def _build_site(self):
        # Create the S3 bucket for the site contents
        self._create_site_bucket()
        


        # Get the hosted zone based on the provided domain name
        hosted_zone = self.__get_hosted_zone()

        # Get an existing or create a new certificate for the site domain
        self.__create_certificate(hosted_zone)

        # Create the cloud front distribution   
        self._create_cloudfront_distribution()

        # Create a Route53 record
        self.__create_route53_record(hosted_zone)
        
        # Attach policy to enable push to S3 website bucket
        self._attach_s3_push_policy()
    def _create_site_bucket(self):
        """a virtual function to be implemented by the sub classes"""

    def _create_cloudfront_distribution(self):
        """a virtual function to be implemented by the sub classes"""
        
    def _attach_s3_push_policy(self):
        """a virtual function to be implemented by the sub classes"""

    def __get_hosted_zone(self):
        return route53.HostedZone.from_lookup(
            self,
            "hosted_zone",
            domain_name=self.__hosted_zone_name,
        )

    def __create_route53_record(self, hosted_zone):
        route53.ARecord(
            self,
            "site-alias-record",
            record_name=self._site_full_domain_name,
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(self.distribution)
            ),
        )

    def __create_certificate(self, hosted_zone):
        if self.__domain_certificate_arn:
            # If certificate arn is provided, import the certificate
            self.certificate = acm.Certificate.from_certificate_arn(
                self,
                "site_certificate",
                certificate_arn=self.__domain_certificate_arn,
            )
        else:
            # If certificate arn is not provided, create a new one.
            # ACM certificates that are used with CloudFront must be in
            # the us-east-1 region.
            self.certificate = acm.DnsValidatedCertificate(
                self,
                "site_certificate",
                domain_name=self._site_full_domain_name,
                hosted_zone=hosted_zone,
                region="us-east-1",
            )


class PublicS3Website(S3Website):
    def __init__(
        self,
        scope,
        construct_id,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)
        self._build_site()

    def _attach_s3_push_policy(self):
        self.group = iam.Group.from_group_name(self, "push-group", self._group_name)
        self.policy = iam.Policy(
            self, "Policy",
            policy_name= self._site_full_domain_name + "s3-websites-push-policy",
            statements=[iam.PolicyStatement(
        actions=[ "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"],
        resources=[self.bucket.bucket_arn, self.bucket.arn_for_objects('*')])])
        self.group.attach_inline_policy(self.policy)

    def _create_site_bucket(self):
        self.bucket = s3.Bucket(
            self,
            "site_bucket",
            bucket_name=self._site_full_domain_name,
            website_index_document=self._website_index_document,
            website_error_document=self._website_error_document,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        bucket_policy = iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[self.bucket.arn_for_objects("*")],
            principals=[iam.AnyPrincipal()],
        )

        self.bucket.add_to_resource_policy(bucket_policy)

    def _create_cloudfront_distribution(self):
        origin_source = cloudfront.CustomOriginConfig(
            domain_name=self.bucket.bucket_website_domain_name,
            origin_protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
            origin_headers={},
        )

        self.distribution = cloudfront.CloudFrontWebDistribution(
            self,
            "cloudfront_distribution",
            viewer_certificate=cloudfront.ViewerCertificate.from_acm_certificate(
                self.certificate,
                aliases=[self._site_full_domain_name],
                security_policy=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2019,
                ssl_method=cloudfront.SSLMethod.SNI,
            ),
            origin_configs=[
                cloudfront.SourceConfiguration(
                    custom_origin_source=origin_source,
                    behaviors=[
                        cloudfront.Behavior(
                            is_default_behavior=True,
                        )
                    ],
                )
            ],
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            price_class=cloudfront.PriceClass.PRICE_CLASS_ALL,
        )
