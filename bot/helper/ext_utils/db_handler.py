import psycopg2
from bot import AUTHORIZED_CHATS, DB_URI, LOGGER, SUDO_USERS


class DbManger:
    def __init__(self):
        self.err = False

    def connect(self):
        try:
            self.conn = psycopg2.connect(DB_URI)
            self.cur = self.conn.cursor()
        except psycopg2.DatabaseError as error:
            LOGGER.error("Error in dbMang : ", error)
            self.err = True

    def disconnect(self):
        self.cur.close()
        self.conn.close()

    def db_auth(self, chat_id: int):
        self.connect()
        if self.err:
            return "There's some error check log for details"
        sql = f'INSERT INTO users VALUES ({chat_id});'
        self.cur.execute(sql)
        self.conn.commit()
        self.disconnect()
        AUTHORIZED_CHATS.add(chat_id)
        return 'Authorized successfully'

    def db_unauth(self, chat_id: int):
        self.connect()
        if self.err:
            return "There's some error check log for details"
        sql = f'DELETE from users where uid = {chat_id};'
        self.cur.execute(sql)
        self.conn.commit()
        self.disconnect()
        AUTHORIZED_CHATS.remove(chat_id)
        return 'Unauthorized successfully'

    def db_addsudo(self, chat_id: int):
        self.connect()
        if self.err:
            return "There's some error check log for details"
        if chat_id in AUTHORIZED_CHATS:
            sql = 'UPDATE users SET sudo = TRUE where uid = {};'.format(
                chat_id
            )
            return self._extracted_from_db_addsudo_10(
                sql, chat_id, 'Successfully promoted as Sudo'
            )

        else:
            sql = f'INSERT INTO users VALUES ({chat_id},TRUE);'
            return self._extracted_from_db_addsudo_10(
                sql, chat_id, 'Successfully Authorized and promoted as Sudo'
            )

    def _extracted_from_db_addsudo_10(self, sql, chat_id, arg2):
        self.cur.execute(sql)
        self.conn.commit()
        self.disconnect()
        SUDO_USERS.add(chat_id)
        return arg2

    def db_rmsudo(self, chat_id: int):
        self.connect()
        if self.err:
            return "There's some error check log for details"
        sql = 'UPDATE users SET sudo = FALSE where uid = {};'.format(
            chat_id
        )
        self.cur.execute(sql)
        self.conn.commit()
        self.disconnect()
        SUDO_USERS.remove(chat_id)
        return 'Successfully removed from Sudo'
