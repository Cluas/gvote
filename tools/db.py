from peewee import MySQLDatabase

from playhouse.migrate import *
from models.users import User
from models.votes import Candidate, Vote, VoteEvent, VoteBanner, CandidateImage
from models.gifts import Gift

database = MySQLDatabase(
    'vote', host="127.0.0.1", port=3306, user="root", password="imyuols123"
)

my_db = MySQLDatabase(
    'vote', host="127.0.0.1", port=3306, user="root", password="imyuols123"

)
migrator = MySQLMigrator(my_db)


def init():
    # 生成表
    database.create_tables([User, Vote])
    database.create_tables([CandidateImage])
    database.create_tables([Candidate,  VoteEvent, VoteBanner, Gift])


if __name__ == "__main__":
    # field = CharField(max_length=200, verbose_name='投票公告', default='')
    # migrate(
    #     migrator.add_column('vote', 'announcement', field),
    #     migrator.add_column('vote', 'title', field),
    #     migrator.add_column('vote', 'description', field),
    # )
    # database.create_tables([VoteBanner])
    init()
