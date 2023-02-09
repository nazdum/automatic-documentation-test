from aws_cdk import aws_iam as iam
from constructs import Construct

class S3WebsiteIAM(Construct):
    def __init__(
        self,
        scope,
        construct_id,
        domain_name,
        sub_domain_name,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)
        
        self._site_domain_name = domain_name 
        self.user = None
        self.group = None
        self.policy = None
        
        if sub_domain_name:
            self._site_domain_name = f"{sub_domain_name}.{domain_name}"
        
        self._create_iam_resources()
    
    def _create_iam_resources(self):
        user_id = self._site_domain_name.replace(".", "-") + "-s3-websites-push-user" 
        self.user = iam.User(self, "s3_push_user", user_name=user_id)
        
        group_id = self._site_domain_name.replace(".", "-") + "-s3-websites-push-group"
        self.group = iam.Group(self, "s3_push_group", group_name=group_id)
        self.user.add_to_group(self.group)
