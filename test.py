from boto3form.aws_ecr import ecr
import sys

if __name__ == "__main__":
    try:
        action = sys.argv[1]
        if action == 'create':
            tags = [
                {
                    'Key': 'created_by',
                    'Value': 's.rukmal'
                },
                {
                    'Key': 'project',
                    'Value': 'alpha1'
                }
            ]
            ecr.ecr_create_handler("<aws_account_number>", "ecr-test-1", tags, image_tag_mutability='IMMUTABLE',
                               scan_on_push=False)

        elif action == 'delete':
            ecr.ecr_delete_handler("<aws_account_number>", "ecr-test-1")

    except IndexError:
        print("Missing arguments pass a valid argument (create or destroy)")

