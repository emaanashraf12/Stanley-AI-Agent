class HandlePackage:

    def can_handle(self, lead):

        return False

    def process(self, session_id, lead, user_message):

        return None


handle_package = HandlePackage()