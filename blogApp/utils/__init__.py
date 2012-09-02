from google.appengine.ext import db


def delete_objects(query):
        cursor = None
        while True:
            q = query
            if cursor is not None:
                q = q.with_cursor(start_cursor=cursor)
            objects = q.fetch(1000)
            cursor = q.cursor()
            l = len(objects)
            db.delete(objects)
            if l < 1000:
                break
