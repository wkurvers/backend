import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker, scoped_session


conn = sqla.create_engine('mysql+pymysql://root:@127.0.0.1/project?host=127.0.0.1?port=3306')

Session = scoped_session(sessionmaker(bind=conn))

Base = declarative_base()


class Persister():
    pass

Base.metadata.create_all(conn)