import boto3
from domain.core.epr.models.base_models import Base
from event.json import json_load
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set the secret name and region
SECRET_NAME = "rds!db-9648e4d7-55cb-4082-b285-08d36827423a"
REGION_NAME = "eu-west-2"  # Adjust as needed


def get_db_credentials():
    """Retrieve database credentials from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=REGION_NAME)
    try:
        # Retrieve the secret
        secret_value = client.get_secret_value(SecretId=SECRET_NAME)

        # Parse the secret value
        secret = json_load(secret_value["SecretString"])
        return secret["username"], secret["password"]
    except Exception as e:
        # print(f"Error retrieving secrets: {e}")
        raise


def get_engine():
    """Create and return a SQLAlchemy engine for PostgreSQL."""
    username, password = get_db_credentials()
    endpoint = "nhse-cpm-b5548ea4-eprv2.c609boclclqd.eu-west-2.rds.amazonaws.com"
    port = "5432"
    db_name = "nhse-cpm-b5548ea4-eprv2"
    # PostgreSQL connection string
    connection_string = (
        f"postgresql://{username}:{password}@{endpoint}:{port}/{db_name}"
    )
    return create_engine(connection_string, echo=False)


def init_db():
    """Create the database file and tables if they don’t exist."""
    engine = get_engine()
    Base.metadata.create_all(engine)


def get_session():
    """Returns a new session."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
