import transaction

class admin:
    """ A collection of useful tools for interacting with your object """
    
    def __init__(self, app):
        self.app = app

    def sync(self):
        """ Sync the changes made by this client with the server """
        self.app._p_jar.sync()

    def commit(self, note=None):
        """ Sync and then commit the changes to this app. You
        can optionally pass through a note """
        txn = transaction.get()
        if note is None:
            note = "Commit from Clouseau"
        txn.note(note)
        txn.commit()
        self.sync()
    