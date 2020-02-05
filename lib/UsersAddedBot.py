from lib.Bot import Bot
from pandas import DataFrame as df

class UsersAddedBot(Bot):
    def __init__(self,userList):

        super().__init__(df(userList), "firstRegistrationMail")

    def getMsg(self, userList):
        return "Successfully added  {} to allowedUsers.csv".format(userList)