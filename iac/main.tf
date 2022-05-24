provider "aws" {
  region = "us-west-2"
}

resource "aws_iam_role" "lambda_role" {
name   = "Gnosis_Safe_SlackBot_Lambda_Function_Role"
assume_role_policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "lambda.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   }
 ]
}
EOF
}
resource "aws_iam_policy" "iam_policy_for_lambda" {
 
 name         = "aws_iam_policy_for_terraform_aws_lambda_role"
 path         = "/"
 description  = "AWS IAM Policy for managing aws lambda role"
 policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": [
       "logs:CreateLogGroup",
       "logs:CreateLogStream",
       "logs:PutLogEvents"
     ],
     "Resource": "arn:aws:logs:*:*:*",
     "Effect": "Allow"
   }
 ]
}
EOF
}
 
resource "aws_iam_role_policy_attachment" "attach_iam_policy_to_iam_role" {
 role        = aws_iam_role.lambda_role.name
 policy_arn  = aws_iam_policy.iam_policy_for_lambda.arn
}

# data "archive_file" "zip_python_dependencies" {
# type        = "zip"
# source_dir  = "${path.module}/../.venv/lib/python3.9/site-packages/"
# output_path = "${path.module}/../app/dependencies.zip"
# }
 
# data "archive_file" "zip_the_python_code" {
# type        = "zip"
# source_dir  = "${path.module}/../app/"
# output_path = "${path.module}/../app/slackbot.zip"
# }

resource "null_resource" "zip_python_code_and_dependencies" {
    provisioner "local-exec" {

    command = "/bin/zsh ../scripts/create_zip.sh"
  }
}
 
resource "aws_lambda_function" "terraform_lambda_func" {
filename                       = "../app/slackbot.zip"
function_name                  = "gnosis_safe_slackbot_lambda_function"
role                           = aws_iam_role.lambda_role.arn
handler                        = "bot.post_slack_message"
runtime                        = "python3.9"
depends_on                     = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role]
}

