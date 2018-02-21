import sys
import json

class dba(object):

    @staticmethod
    def _query(query, params, database):
        out = []
        # con = database.connect()
        cur = database.execute_sql(query, params)
        rows = cur.fetchall()

        for row in rows:
            out.append(dba._row_to_dict(cur, row))

        try:
            pass
        except:
            out = []

        return out


    @staticmethod
    def _row_to_dict(cursor, row):
        out = {}

        description = cursor.description
        columns = [t[0][t[0].find('.') + 1:] for t in description]
        ncols = len(description)

        for i in range(ncols):
            out[columns[i]] = row[i]

        return out

    @staticmethod
    def dict(query, params, database):
        return dba._query( query, params, database )

    @staticmethod
    def json(query, params, database):
        return json.dumps( dba._query( query, params, database) )

    @staticmethod
    def scalar(query, params, database):
        try:
            cur = database.execute_sql(query, params)
            rows = cur.fetchone()[0]
        except:
            rows = 0;
        return rows

    @staticmethod
    def empty(query, params, database):
        last_id = None
        row_count = None
        try:
            con = database.connect()
            cur = database.execute_sql(query, params)

            cur.execute(query, params)

            last_id =  cur.lastrowid
            row_count = cur.rowcount

            con.commit()
        except:
            last_id =  -1
            row_count = -1
        finally:
            if con:
                con.close();
        return last_id, row_count

    @staticmethod
    def transaction(queries, database):
        result = []
        try:
            con = Config.DATABASE.connect()

            for query in queries:
                sql, params = query
                cur = database.execute_sql(query, params)
                rows = cur.fetchall()

                cur.execute(sql, params)
                result.append( (cur.lastrowid, cur.rowcount) )
            con.commit()
        except:
            if con:
                con.rollback()
        finally:
            if con:
                con.close()

        return result
