import databases
import sqlalchemy
from src.config import config
from src.model import Status


metadata = sqlalchemy.MetaData()


tasks_table = sqlalchemy.Table(
    "tasks",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("creation_date", sqlalchemy.Date, nullable=False),
    sqlalchemy.Column("due_date", sqlalchemy.Date, nullable=True),
    sqlalchemy.Column("status", sqlalchemy.Enum(Status), nullable=False),
    sqlalchemy.Column("completed_ts", sqlalchemy.DateTime, nullable=True),
)


engine = sqlalchemy.create_engine(config.DATABASE_URL)
metadata.create_all(engine)
database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK
)
