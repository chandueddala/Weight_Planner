"""
AWS Session and DynamoDB Table Management
Provides centralized, environment-based boto3 session configuration.
"""
import os
import boto3
from typing import Tuple


def get_boto3_session() -> boto3.Session:
    """
    Create a boto3 session using environment configuration.
    
    Environment variables:
        AWS_PROFILE: AWS CLI profile name (default: 'default')
        AWS_REGION: AWS region (default: 'us-east-2')
    
    Returns:
        boto3.Session configured with profile and region
    """
    profile = os.getenv("AWS_PROFILE", "default")
    region = os.getenv("AWS_REGION", "us-east-2")
    
    return boto3.Session(profile_name=profile, region_name=region)


def get_ddb_tables() -> Tuple[object, object, object]:
    """
    Get DynamoDB table resources for Users, UserSessions, and UserMessages.
    
    Environment variables:
        DDB_USERS_TABLE: Users table name (default: 'Users')
        DDB_SESSIONS_TABLE: UserSessions table name (default: 'UserSessions')
        DDB_MESSAGES_TABLE: UserMessages table name (default: 'UserMessages')
    
    Returns:
        Tuple of (users_table, sessions_table, messages_table)
    """
    session = get_boto3_session()
    ddb = session.resource("dynamodb")
    
    users_table_name = os.getenv("DDB_USERS_TABLE", "Users")
    sessions_table_name = os.getenv("DDB_SESSIONS_TABLE", "UserSessions")
    messages_table_name = os.getenv("DDB_MESSAGES_TABLE", "UserMessages")
    
    users_table = ddb.Table(users_table_name)
    sessions_table = ddb.Table(sessions_table_name)
    messages_table = ddb.Table(messages_table_name)
    
    return users_table, sessions_table, messages_table
