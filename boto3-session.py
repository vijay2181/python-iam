import os
import boto3

class AWSSession:
    def __init__(self):
        self.profile = os.environ.get('AWS_PROFILE')
        self.region = os.environ.get('AWS_REGION')

    def get_session(self):
        session = boto3.Session(profile_name=self.profile, region_name=self.region)
        return session

# Example usage
if __name__ == '__main__':
    aws_session = AWSSession()
    session = aws_session.get_session()
    print(f"Profile: {session.profile_name}")
    print(f"Region: {session.region_name}")
