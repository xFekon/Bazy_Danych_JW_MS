class Session:
    current_user_id = None
    current_username = None

    @staticmethod
    def login(user_id, username):
        Session.current_user_id = user_id
        Session.current_username = username

    @staticmethod
    def logout():
        Session.current_user_id = None
        Session.current_username = None