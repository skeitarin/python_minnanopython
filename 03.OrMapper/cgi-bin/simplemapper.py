import sqlite3

class BaseMapper(object):
    rows=()
    connection=sqlite3.connect('./test.sqlite')

    def __init__(self, **kws):
        # self.connection=sqlite3.connect(db_path)
        """
        クラスを初期化する
        idを引数に渡された場合は，既存データをSELECTして返す
        その他のキーワード引数を渡された場合は，データをDBにInsertする
        """
        if "id" in kws.keys():
            rownames=[v[0] for v in self.__class__.rows]
            rownamestr=', '.join(rownames)
            cn=self.__class__.__name__
            sql="""SELECT {columns} FROM {table_name} WHERE id=?""".format(columns=rownamestr, table_name=cn)
            cur=self.get_connection().cursor()
            cur.execute(sql, (kws['id'],))
            for rowname, v in zip(rownames, cur.fetchone()):
                setattr(self, rowname, v)
            self.id=kws['id']
            cur.close()
        elif kws:
            self.id=self.insert(**kws)
            rownames=[v[0] for v in self.__class__.rows]
            for k in kws.keys():
                if k in rownames:
                    setattr(self, k, kws[k])
    
    def __repr__(self):
        """
        オブジェクトの文字列表記を定義
        """
        rep=str(self.__class__.__name__)+':'
        rownames=[v[0] for v in self.__class__.rows]
        rep+=', '.join(["%s=%s"%(x, repr(getattr(self, x))) for x in rownames])
        return "<%s>"%rep
    
    @classmethod
    def set_connection(cls, con):
        cls.connection=con
    
    @classmethod
    def get_connection(cls):
        return cls.connection

    @classmethod
    def create(cls, ignore_error=False):
        sql="""CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, {columns});"""
        columns=' ,'.join(["{c} {d}".format(c=c, d=d) for c, d in cls.rows ])
        sql=sql.format(table_name=cls.__name__, columns=columns)
        cur=cls.get_connection().cursor()
        try:
            cur.execute(sql)
            cls.get_connection().commit()
        except Exception as e:
            if not ignore_error:
                raise e
            cls.get_connection().rollback()
        finally:
            cur.close()
    
    @classmethod
    def insert(cls, **kws):
        sql="""INSERT INTO {table_name}({columns}) VALUES({holders})"""
        rownames=' ,'.join(["{rowname}".format(rowname=row[0]) for row in cls.rows])
        holders=' ,'.join(["?" for row in cls.rows])
        sql=sql.format(table_name=cls.__name__, columns=rownames, holders=holders)
        values=[kws[v[0]] for v in cls.rows]
        cur=cls.get_connection().cursor()
        cur.execute(sql, values)
        cur.execute("SELECT max(id) FROM {table_name}".format(table_name=cls.__name__))
        new_id=cur.fetchone()[0]
        cls.get_connection().commit()
        cur.close()
        return new_id

    def update(self):
        """
        データを更新する
        """
        sql="""UPDATE %s SET %s WHERE id=?"""
        rownames=[v[0] for v in self.__class__.rows]
        holders=', '.join(['%s=?'%v for v in rownames])
        sql=sql%(self.__class__.__name__, holders)
        values=[getattr(self, n) for n in rownames]
        values.append(self.id)
        cur=self.get_connection().cursor()
        cur.execute(sql, values)
        self.get_connection().commit()
        cur.close()
    
    where_conditions={                      # (1)
        '_gt':'>', '_lt':'<',
        '_gte':'>=', '_lte':'<=',
        '_like':'LIKE' }

    @classmethod
    def select(cls, **kws):
        """
        テーブルからデータをSELECTする
        """
        order=''
        if "order_by" in kws.keys():
            order=" ORDER BY "+kws['order_by']
            del kws['order_by']
        where=[]
        values=[]
        for key in kws.keys():
            ct='='
            kwkeys=cls.where_conditions.keys()
            for ckey in kwkeys:
                if key.endswith(ckey):
                    ct=cls.where_conditions[ckey]
                    kws[key.replace(ckey, '')]=kws[key]
                    del kws[key]
                    key=key.replace(ckey, '')
                    break
            where.append(' '.join((key, ct, '? ')))
            values.append(kws[key])
        wherestr="AND ".join(where)
        sql="SELECT id FROM "+cls.__name__
        if wherestr:
            sql+=" WHERE "+wherestr
        sql+=order
        cur=cls.get_connection().cursor()
        cur.execute(sql, values)
        for item in cur.fetchall():
            ins= cls(id=item[0])
            yield ins                      # (2)
        cur.close()