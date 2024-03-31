from json import JSONDecodeError
import boto3
import json
import os


def ecr_create_handler(registry_id, repository_name, tags, image_tag_mutability='IMMUTABLE', scan_on_push=True,
                       encryption_type='AES256', kms_key_id=None):
    create_repository = False
    delete_repository = False
    state_file_location = 'state.json'
    state_in = {}
    number_of_changes = 0
    ecr = boto3.client('ecr')
    if encryption_type == 'AES256':
        encryption_configuration = {
            'encryptionType': encryption_type
        }
    elif encryption_type == 'KMS':
        if kms_key_id is None:
            raise Exception('KMS key is not provided')
        else:
            encryption_configuration = {
                'encryptionType': encryption_type,
                'kmsKeyId': kms_key_id
            }
    else:
        raise Exception('Invalid encryption Type. Valid values are AES256 and KMS')

    try:
        with open(state_file_location, 'r') as openfile:
            state_in = json.load(openfile)
    except FileNotFoundError:
        create_state_file()
    except JSONDecodeError:
        create_state_file()

    if "repository" in state_in:

        repository = state_in['repository']
        is_tag_changed = check_tags_changes(repository['tags'], tags)
        print(is_tag_changed)
        image_tag_mutability_state = repository['imageTagMutability']
        repository_name_state = repository['repositoryName']
        scan_on_push_state = repository['imageScanningConfiguration']['scanOnPush']
        encryption_type_state = repository['imageScanningConfiguration']['encryptionType']
        if image_tag_mutability_state != image_tag_mutability:
            print("Image tag mutability has changed.")
            number_of_changes += 1
            ecr.put_image_tag_mutability(
                registryId=registry_id,
                repositoryName=repository_name,
                imageTagMutability=image_tag_mutability
            )
            state_in['repository']['imageTagMutability'] = image_tag_mutability

        if repository_name_state != repository_name:
            print("Repository name has changed.")
            number_of_changes += 1
            delete_repository = True

        if scan_on_push_state != scan_on_push:
            print("Repository image scanning configuration has changed.")
            number_of_changes += 1
            delete_repository = True

        if is_tag_changed:
            number_of_changes += 1
            ecr.tag_resource(
                resourceArn=repository['repositoryArn'],
                tags=tags
            )
            state_in['repository']['tags'] = tags

        if encryption_type_state != encryption_type:
            print("Repository encryption type has changed.")
            number_of_changes += 1
            delete_repository = True

    else:
        create_repository = True

    if delete_repository:
        ecr.delete_repository(
            registryId=registry_id,
            repositoryName=repository_name_state,
            force=True
        )
        print("Repository has been deleted.")
        create_repository = True

    if create_repository:
        response = ecr.create_repository(
            registryId=registry_id,
            repositoryName=repository_name,
            tags=tags,
            imageTagMutability=image_tag_mutability,
            imageScanningConfiguration={
                'scanOnPush': scan_on_push
            },
            encryptionConfiguration=encryption_configuration
        )
        del response['repository']['createdAt']
        response['repository']['tags'] = tags
        state_out = json.dumps(response, indent=4)
        with open(state_file_location, "w") as outfile:
            outfile.write(state_out)
        print("Repository created successfully")
    else:
        if number_of_changes == 0:
            print("No changes detected.")
        else:
            print("{} Changes detected.".format(number_of_changes))
            state_out = json.dumps(state_in, indent=4)
            with open(state_file_location, "w") as outfile:
                outfile.write(state_out)
            print("Changes applied successfully.")


def ecr_delete_handler(registry_id, repository_name):
    ecr = boto3.client('ecr')

    state_file_location = 'state.json'
    with open(state_file_location, 'r') as openfile:
        state_in = json.load(openfile)

    if "repository" in state_in:
        repository = state_in['repository']
        repository_name_state = repository['repositoryName']
        if repository_name_state == repository_name:
            ecr.delete_repository(
                registryId=registry_id,
                repositoryName=repository_name_state,
                force=True
            )
            open(state_file_location, 'w').close()
            print("Repository has been deleted.")
        else:
            print("No repository found {}".format(repository_name))
    else:
        print("No repository found {}".format(repository_name))


def create_state_file():
    current_dir = os.path.dirname(__file__)
    state_file_location = os.path.join(current_dir, 'state.json')
    # state_file_location = 'state.json'
    print(state_file_location)
    with open(state_file_location, "w") as outfile:
        json.dump({}, outfile, indent=4)


def check_tags_changes(state_tags, input_tags):
    tag_changed = False
    if len(input_tags) != len(state_tags):
        tag_changed = True
        return tag_changed
    else:
        for i in range(len(state_tags)):
            if state_tags[i]['Key'] != input_tags[i]['Key']:
                tag_changed = True
                break
            if state_tags[i]['Value'] != input_tags[i]['Value']:
                tag_changed = True
                break

        return tag_changed
