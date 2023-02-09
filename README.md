# Setting up CDK App AWS IAM User and permissions
In order to run this CDK App you must first set up an AWS IAM User with programatic access (with valid `ACCESS_KEY_ID` & `SECRET_ACCESS_KEY` tokens) on the account you want to use to deploy the resources the CDK App creates.

Note: The created AWS IAM User needs a policy attached to it with the following permissions:


    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                "sts:AssumeRole"
                ],
                "Resource": [
                "arn:aws:iam::*:role/cdk-*"
                ]
            }
        ]
    }

This policy allows the mentioned AWS IAM User to be able to deploy all the CDK App resources on cdk deployment phase.

Once the user is correctly set up, open a terminal in the machine where AWS CDK is going to be run and set up the previously obtained tokens (`ACCESS_KEY_ID` & `SECRET_ACCESS_KEY` tokens) by running:

    aws configure

Make sure to set up the correct region when interacting with the previous command output.

# CDK Stack parameters
This CDK stack requires only one parameter:

> website: This parameter specifies the hostname we want people to use in order to access our S3 HTML website ex: site.test.com

# Deploying the CDK Stack
After successfully setting up all the previous requirements, CDK deployment can start, make sure to follow along the next steps:

 1. Run the `cdksetup.sh` file included in the repository this will install AWS CDK and its dependencies
 2. Run `pip install -r requirements.txt` at the root of the project folder (use venv to avoid unwanted global dependencies)
 3. Make sure you have configured proper AWS credentials with `aws configure` 
 4. Run `cdk bootstrap --context website=<WEBSITE_URL>` if it's your first time running CDK (this command is used to deploy aux AWS resources to hold things like Lambda Code, Policies, etc that are going to be used on the deployment), make sure you have `AdministratorAccess` when running this command.
 5. Run `cdk deploy --context website=<WEBSITE_URL> --require-approval never` to start the deployment process, the `--require-approval never` parameter is set to avoid manual input for CDK deploy confirmation.

    `Ex: cdk deploy --context website=test.com`
    creates test.com, alpha.test.com, beta.test.com



# Destroying the CDK stack
In order to delete any existing stack created with this CDK app you must run the `cdk destroy` command with the following syntax:

`cdk destroy --context website=<WEBSITE_URL>`

Ex: `cdk destroy --context website=test.com`

This action will successfully delete the previously created stack

> Advice: Stack deletion can take several minutes, it is recommended to run `cdk destroy` tasks in parallel if you have the intention of deleting multiple Stacks.
