import click
import random
import string
from session import AWSSession
from tabulate import tabulate
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

PASSWORD_CHOICES = string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation

class IAMManager:
    def __init__(self, session):
        self.iam = session.client('iam')

    def get_signin_url(self, client):
        try:
            account_alias = client.list_account_aliases()['AccountAliases'][0]
            sign_in_url = f"https://{account_alias}.signin.aws.amazon.com/console/"
            return sign_in_url
        except ClientError as err:
            click.echo(f"Failed to get the sign_in_url: {err}")
            return None


    def create_user(self, username, groupname):
        if username is None:
            click.echo("Error: The '--user' argument is required to create a user.")
            return
        if groupname is None:
            click.echo("Error: The '--groupname' argument is required to create a user.")
            return

        try:
            # Check if the group exists
            existing_groups = self.iam.list_groups()['Groups']
            existing_groupnames = [group['GroupName'] for group in existing_groups]
            if groupname not in existing_groupnames:
                raise ValueError(f"Group '{groupname}' does not exist.")

            # Check if the user already exists
            existing_users = self.iam.list_users()['Users']
            existing_usernames = [user['UserName'] for user in existing_users]
            if username in existing_usernames:
                raise ValueError(f"User '{username}' already exists.")

            # Create the user
            response = self.iam.create_user(UserName=username)
            user = response['User']
            access_keys = self.iam.create_access_key(UserName=username)['AccessKey']
            password = ''.join(random.choices(PASSWORD_CHOICES, k=16))
            self.iam.create_login_profile(UserName=username, Password=password, PasswordResetRequired=True)
            self.iam.add_user_to_group(UserName=username, GroupName=groupname)

            # Prepare the data for tabular display
            data = [
                {"Field": "AWS URL", "Value": self.get_signin_url(self.iam)},
                {"Field": "Username", "Value": username},
                {"Field": "Temporary password", "Value": password},
                {"Field": "Access key ID", "Value": access_keys['AccessKeyId']},
                {"Field": "Secret access key", "Value": access_keys['SecretAccessKey']}
            ]

            # Display the details in tabular format
            click.echo("User created successfully.")
            click.echo("Details:")
            click.echo(tabulate(data, headers="keys", tablefmt="fancy_grid"))

        except ClientError as err:
            click.echo(f"An error occurred: {err}")
        except ValueError as err:
            click.echo(f"Error: {err}")


    def delete_user(self, username):
        try:
            response = self.iam.list_groups_for_user(UserName=username)
            groups = response['Groups']
            for group in groups:
                self.iam.remove_user_from_group(GroupName=group['GroupName'], UserName=username)
            try:
                self.iam.delete_login_profile(UserName=username)
            except self.iam.exceptions.NoSuchEntityException:
                pass
            response = self.iam.list_access_keys(UserName=username)
            access_keys = response['AccessKeyMetadata']
            for key in access_keys:
                self.iam.delete_access_key(UserName=username, AccessKeyId=key['AccessKeyId'])
            self.iam.delete_user(UserName=username)
            click.echo(f"User '{username}' deleted successfully.")
        except ClientError as err:
            click.echo(f"An error occurred: {err}")


    def list_users(self, groupname=None):
        try:
            if groupname:
                response = self.iam.get_group(GroupName=groupname)
                users = response['Users']
                user_names = [user['UserName'] for user in users]
            else:
                response = self.iam.list_users()
                users = response['Users']
                user_names = [user['UserName'] for user in users]

            click.echo(tabulate({"Users": user_names}, headers="keys", tablefmt="fancy_grid"))
        except ClientError as err:
            click.echo(f"An error occurred: {err}")


    def list_groups(self):
        response = self.iam.list_groups()
        groups = response['Groups']
        group_names = [group['GroupName'] for group in groups]
        table = {"Groups": group_names}
        click.echo(tabulate(table, headers="keys", tablefmt="fancy_grid"))


    def list_groups_for_user(self, username):
        if not username:
            click.echo("Error: The '--user' argument is required to list groups for a user.")
            return

        try:
            response = self.iam.list_groups_for_user(UserName=username)
            groups = response['Groups']
            if groups:
                headers = ['Group Name', 'Group ID']
                table = [[group['GroupName'], group['GroupId']] for group in groups]
                click.echo(tabulate(table, headers=headers, tablefmt="fancy_grid"))
            else:
                click.echo(f"No groups found for the user '{username}'.")
        except self.iam.exceptions.NoSuchEntityException:
            click.echo(f"The user with name '{username}' cannot be found.")
        except ClientError as e:
            click.echo(f"An error occurred: {e}")


    def password_reset(self, username):
        if not username:
            click.echo("Error: The '--user' argument is required to reset password for a user.")
            return

        try:
            # Reset the console password
            password = ''.join(random.choices(PASSWORD_CHOICES, k=16))
            self.iam.update_login_profile(UserName=username, Password=password, PasswordResetRequired=True)
            click.echo("Console password reset successfully.")

            # Display the reset password in tabular format
            table = [["Field", "Value"],
                     ["Username", username],
                     ["Temporary password", password]]
            click.echo(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

        except ClientError as err:
            click.echo(f"An error occurred: {err}")


    def list_access_keys(self, username):
        if not username:
            click.echo("Error: The '--user' argument is required to list access keys for a user.")
            return

        try:
            # Retrieve the access keys for the user
            response = self.iam.list_access_keys(UserName=username)
            access_keys = response['AccessKeyMetadata']

            if not access_keys:
                click.echo(f"No access keys found for user '{username}'.")
                return

            # Display the access keys in tabular format
            table = [["Access Key ID", "Status", "Created", "Age (days)"]]
            for key in access_keys:
                access_key_id = key['AccessKeyId']
                status = key['Status']
                created = key['CreateDate']
                age = (datetime.now(created.tzinfo) - created).days
                created_str = created.strftime("%Y-%m-%d %H:%M:%S")
                table.append([access_key_id, status, created_str, age])

            click.echo(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

        except Exception as e:
            click.echo(f"An error occurred: {str(e)}")

    def create_access_key(self, username):
        try:
            response = self.iam.create_access_key(UserName=username)
            access_key = response['AccessKey']
            click.echo("New access key created successfully.")
            click.echo("Details:")
            click.echo(f"Access Key ID: {access_key['AccessKeyId']}")
            click.echo(f"Secret Access Key: {access_key['SecretAccessKey']}")
        except ClientError as err:
            click.echo(f"An error occurred: {err}")

    def delete_access_key(self, username, access_key_id):
        try:
            self.iam.delete_access_key(UserName=username, AccessKeyId=access_key_id)
            click.echo(f"Deleted access key '{access_key_id}' for user '{username}'.")
        except ClientError as err:
            click.echo(f"An error occurred: {err}")


    def rotate_access_keys(self, username):
        if not username:
            click.echo("Error: The '--user' argument is required to rotate access keys for a user.")
            
            return
        try:
            # Retrieve the access keys for the user
            response = self.iam.list_access_keys(UserName=username)
            access_keys = response['AccessKeyMetadata']

            if not access_keys:
                click.echo(f"No access keys found for user '{username}'.")
                return

            # Sort the access keys by creation date
            sorted_keys = sorted(access_keys, key=lambda k: k['CreateDate'])

            if len(sorted_keys) == 1:
                # User has only one pair of keys, delete and create new ones
                access_key_id = sorted_keys[0]['AccessKeyId']
                self.iam.delete_access_key(UserName=username, AccessKeyId=access_key_id)
                click.echo(f"Deleted access key '{access_key_id}' for user '{username}'.")
                self.create_access_key(username)
            elif len(sorted_keys) >= 2:
                # User has two or more pairs of keys, delete the oldest one
                access_key_id = sorted_keys[0]['AccessKeyId']
                self.iam.delete_access_key(UserName=username, AccessKeyId=access_key_id)
                click.echo(f"Deleted oldest access key '{access_key_id}' for user '{username}'.")
            else:
                click.echo(f"Unexpected number of access keys found for user '{username}'.")

            # List the remaining access keys for the user
            self.list_access_keys(username)

        except ClientError as e:
            click.echo(f"An error occurred: {str(e)}")

    def remove_user_from_group(self, username, groupname):
        if not username:
            click.echo("Error: The '--user' argument is required to remove a user from a group.")
            return

        if not groupname:
            click.echo("Error: The '--groupname' argument is required to remove a user from a group.")
            return

        try:
            self.iam.remove_user_from_group(GroupName=groupname, UserName=username)
            click.echo(f"User '{username}' removed from group '{groupname}' successfully.")
        except self.iam.exceptions.NoSuchEntityException:
            click.echo(f"The user with name '{username}' or group with name '{groupname}' cannot be found.")
        except ClientError as e:
            click.echo(f"An error occurred: {str(e)}")



@click.group()
@click.pass_context
def cli(ctx):
    aws_session = AWSSession()
    session = aws_session.get_session()
    ctx.obj = IAMManager(session)

@cli.command()
@click.option('--user', help='Username')
@click.option('--groupname', help='Specify the groupname for the user.')
@click.pass_obj
def create_user(obj, user, groupname):
    obj.create_user(user, groupname)


@cli.command()
@click.argument('username')
@click.pass_obj
def delete_user(obj, username):
    obj.delete_user(username)

@cli.command()
@click.pass_obj
def list_groups(obj):
    obj.list_groups()

@cli.command()
@click.option('--groupname', help='Specify the groupname to filter users.')
@click.pass_obj
def list_users(obj, groupname=None):
    obj.list_users(groupname)


@cli.command()
@click.option('--user', help='Username')
@click.pass_obj
def list_groups_for_user(obj, user):
    obj.list_groups_for_user(user)


@cli.command()
@click.option('--user', help='Username')
@click.pass_obj
def password_reset(obj, user):
    obj.password_reset(user)


@cli.command()
@click.option('--user', help='Username')
@click.pass_obj
def list_access_keys(obj, user):
    obj.list_access_keys(user)


@cli.command()
@click.option('--user', help='Username')
@click.pass_obj
def rotate_access_keys(obj, user):
    obj.rotate_access_keys(user)

@cli.command()
@click.option('--user', help='Username')
@click.option('--groupname', help='Specify the groupname for the user.')
@click.pass_obj
def remove_user_from_group(obj, user, groupname):
    obj.remove_user_from_group(user, groupname)


if __name__ == '__main__':
    cli()
