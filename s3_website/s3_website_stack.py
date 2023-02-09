from aws_cdk import CfnOutput, Stack

from s3_website.s3_website_construct import PublicS3Website
from s3_website.s3_website_iam_construct import S3WebsiteIAM


class S3WebsiteStack(Stack):
    def __init__(self, scope, construct_id: str, props, **kwargs) -> None:
        website_full_name = props["sub_domain_name"] + "." + props["domain_name"] if props["sub_domain_name"] else props["domain_name"]
        
        super().__init__(scope, construct_id, tags={"website": website_full_name}, **kwargs)

        production_construct_id = "-".join(["production", construct_id])
        alpha_construct_id = "-".join(["alpha", construct_id])
        beta_construct_id = "-".join(["beta", construct_id])
        
        
        iam_resources = S3WebsiteIAM(
            self,
            "iam-" + construct_id,
            domain_name= props["domain_name"],
            sub_domain_name = props["sub_domain_name"]
        )
        production_site = PublicS3Website(
            self,
            production_construct_id,    
            domain_certificate_arn=props["domain_certificate_arn"],
            website_index_document="index.html",
            website_error_document="404.html",
            sub_domain_name=props["sub_domain_name"],
            domain_name=props["domain_name"],
            environment="production",
        )
        
        alpha_site = PublicS3Website(
            self,
            alpha_construct_id,    
            domain_certificate_arn=props["domain_certificate_arn"],
            website_index_document="index.html",
            website_error_document="404.html",
            sub_domain_name=props["sub_domain_name"],
            domain_name=props["domain_name"],
            environment="alpha",
        )
        
        beta_site = PublicS3Website(
            self,
            beta_construct_id,   
            domain_certificate_arn=props["domain_certificate_arn"],
            website_index_document="index.html",
            website_error_document="404.html",
            sub_domain_name=props["sub_domain_name"],
            domain_name=props["domain_name"],
            environment="beta",
        )
        
        production_site.node.add_dependency(iam_resources)
        alpha_site.node.add_dependency(iam_resources)
        beta_site.node.add_dependency(iam_resources)

        
        

