import sqlite3
from configQuotes import Config
import time
from .user import User
import favicon
import os

config = Config()

def format_time(difference): 
    # convert the unix time into a more readable format probably a way easier way of doing this 
    minutes = int(difference / 60)
    if (minutes < 60):
        return str(minutes) + " minutes ago"
    else:
        hours = int(minutes / 60)

        if (hours < 24):
            return str(hours) + " hours ago"
        
        else:
            days = int(hours / 24)

            return str(days) + " days ago"

class List:
    
    def __init__(self):
        self.dbPath = config.dbName

    def addList(self,name,description,sites,id_users):
        with sqlite3.connect(self.dbPath) as con:
            cur = con.cursor()

            cur.execute("SELECT id FROM lists where name = ?",[name])
            listsWithSameName = cur.fetchone() # if a list already exists with the same name

            if (not listsWithSameName):
                
                cur.execute("INSERT INTO lists (id_users,name,description,time_submitted) VALUES (?,?,?,?)",(id_users,name,description,time.time()))

                list_id = cur.lastrowid

                if sites != "": # if new sites has list
                    sitelist = sites.split(", ")
                    for url in sitelist:
                        cur.execute("SELECT id FROM sites WHERE url = ?",[url])
                        site_id = cur.fetchone()[0]

                        if not site_id: # if site not already in the database 
                            found_icons = favicon.get(url)
                            best_icon = found_icons[0][0]
                            cur.execute("INSERT INTO sites (sitename,url,favicon_url) VALUES (?,?,?)",("test", url, best_icon))
                            site_id = cur.lastrowid
                            
                        cur.execute("INSERT INTO lists_sites (id_sites,id_lists) VALUES(?,?)",(site_id,list_id)) # link site_id to the new list"""
                
                con.commit()
                cur.close()

                return True
            else:
                return False
    
    def retrieveAllLists(self):

        with sqlite3.connect(self.dbPath) as con:

            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM lists ORDER BY time_submitted DESC")
            result = cur.fetchall()
            cur.close()

            if result:
                return result
            else:
                return False


    def retrieveListByName(self, list_name):
        with sqlite3.connect(self.dbPath) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM lists WHERE name =?", [list_name])
            result = cur.fetchone()[0]
            cur.close()
            
            if result:
                return result
            else:
                return False

    def retrieveSites(self, list_id):
        with sqlite3.connect(self.dbPath) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT id_sites FROM lists_sites WHERE id_lists = ?",[list_id])       
            site_ids = cur.fetchall()
            
            if site_ids:
                results = []
                for site_id in site_ids:
                    cur.execute("SELECT * FROM sites WHERE id = ?", [site_id[0]])
                    results.append(cur.fetchone())

                cur.close()
                return results

            else:
                return False

    def retrieveUserLists(self, user_name):

        with sqlite3.connect(self.dbPath) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM users WHERE username = ?", [user_name])
            user_id = cur.fetchone()[0]
            cur.execute("SELECT * FROM lists WHERE id_users = ? ORDER BY time_submitted DESC",[user_id])
            result = cur.fetchall()
            cur.close()

            if result:
                return result
            else:
                return False

    def deleteList(self, userid, listname):
        with sqlite3.connect(self.dbPath) as con:

            cur = con.cursor()
            cur.execute("SELECT * FROM lists WHERE id_users = ? AND name = ?",[userid, listname])
            result = cur.fetchone()

            if result:
                cur.execute("DELETE FROM lists WHERE name = ?",[listname])
                listid = self.retrieveListByName(listname)
                cur.execute("DELETE FROM lists_sites WHERE id_lists = ?",[listid])
                cur.close()
                return True
            else:
                cur.close()
                return False

    def deleteSiteFromList(self, siteid, listid):
        with sqlite3.connect(self.dbPath) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()

            cur.execute("DELETE FROM lists_sites where id_sites = ? AND id_lists = ?", [siteid,listid] )

    def addSite(self, siteurl, listid):
        with sqlite3.connect(self.dbPath) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            
            if siteurl != "":
                url = os.path.dirname(siteurl)
                cur.execute("SELECT id FROM sites WHERE url = ?",[url])
                e = cur.fetchone()

                if e:
                    site_id = e[0]

                else: # if site not already in the database 
                    found_icons = favicon.get(url)
                    best_icon = found_icons[0][0]
                    cur.execute("INSERT INTO sites (sitename,url,favicon_url) VALUES (?,?,?)",("test", url, best_icon))
                    site_id = cur.lastrowid
                    
                cur.execute("INSERT INTO lists_sites (id_sites,id_lists) VALUES(?,?)",(site_id,listid)) # link site_id to the new list"""


    def getExtraInfo(self, lists):
        listsInfo = []
        user = User()
        if lists:
            for list in lists:
                info = {}
                difference = int((time.time() - float(list['time_submitted'])))
                info["time"] = format_time(difference)

                info["name"] = user.getNameFromId(list['id_users'])
                
                sites = self.retrieveSites(list["id"])

                if sites:
                    site_icons = []
                    for site in sites:
                        site_icons.append(site['favicon_url'])
                    info["site_icons"] = site_icons

                listsInfo.append(info)

            return listsInfo

        return False

            