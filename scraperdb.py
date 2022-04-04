from xml.etree import ElementTree
import pyodbc
import time


def getdbconnection(server, dbname, dbusr, dbpw):
    database = dbname
    username = dbusr
    password = dbpw
    driver = '{ODBC Driver 17 for SQL Server}'
    connection = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username + ';PWD=' + password)
    return connection


def updateTableFromCSV(conn, tablename, data):
    mycursor = conn.cursor()
    try:
        start = time.time()
        mycursor.fast_executemany = True
        records = ElementTree.fromstring(data).findall('Record')
        columnlist = []
        rows = []
        values = []
        newlist = []
        columnstype = ""
        columns = ""
        columnsymbols = ""
        count = 0

        for item in records[0]:
            for element in item.iter():
                columnlist.append(element.tag.lower()[0:127])

        for i, v in enumerate(columnlist):
            totalcount = columnlist.count(v)
            count = columnlist[:i].count(v)
            newlist.append(v + str(count + 1) if totalcount > 1 else v)

        for element in newlist:
            columns += element + ", "
            columnstype += element + " varchar(3000), "
            columnsymbols += "?, "

        columns = columns[:-2].replace('-', '_').replace(".", "")
        columnstype = columnstype[:-2].replace('-', '_').replace(".", "")
        columnsymbols = columnsymbols[:-2]

        try:
            mycursor.execute('DROP TABLE IF EXISTS ' + tablename)
            mycursor.execute('CREATE TABLE ' + tablename + ' (' + columnstype + ')')
        except Exception as e:
            print(e)
            mycursor.execute('CREATE TABLE ' + tablename + ' (' + columnstype + ')')
        stmt = "INSERT INTO " + tablename + " (" + columns + ") VALUES (" + columnsymbols + ")"

        for item in records:
            for element in item.iter():
                if element.tag != "Record":
                    values.append(str(element.text or "").replace(",", "").replace("'", "").replace('"', "").replace("\\", ""))
            count += 1
            rows.append(values)
            values = []
            if len(rows) > 5000:
                mycursor.executemany(stmt, rows)
                rows = []

        mycursor.executemany(stmt, rows)
        mycursor.commit()
        mycursor.close()
        print(str(count) + " rows added to " + tablename + " in: " + str(time.time() - start))
        return True
    except Exception as e:
        print("Exception:")
        print(e)
        mycursor.close()
        return False
