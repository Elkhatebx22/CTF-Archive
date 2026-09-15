class db:
    """My Module executes developer-freindly SQL statements with a strong security check"""
    sql_terms = [
        "ADD", "ALL", "ALTER", "AND", "ANY", "AS", "ASC", "BACKUP", "BETWEEN",
        "BY", "CASE", "CHECK", "COLUMN", "CONSTRAINT", "CREATE", "DATABASE", "DEFAULT",
        "DELETE", "DESC", "DISTINCT", "DROP", "EXEC", "EXISTS", "FOREIGN", "FROM",
        "FULL", "GROUP", "HAVING", "IN", "INDEX", "INNER", "INSERT", "INTO", "IS",
        "JOIN", "LEFT", "LIKE", "LIMIT", "NOT", "NULL", "ON", "OR", "ORDER",
        "OUTER", "PRIMARY", "PROCEDURE", "RIGHT", "ROWNUM", "SELECT", "SET", "TABLE",
        "TOP", "TRUNCATE", "UNION", "UNIQUE", "UPDATE", "VALUES", "VIEW", "WHERE",
        "ABS", "AVG", "CHAR", "CHR", "COALESCE", "COUNT", "DATE", "DATETIME",
        "GLOB", "GROUP_CONCAT", "HEX", "IFNULL", "INSTR", "LENGTH", "LIKE", "LOWER",
        "LTRIM", "MAX", "MIN", "NULLIF", "PRINTF", "QUOTE", "RANDOM", "RANDOMBLOB",
        "REPLACE", "ROUND", "RTRIM", "SIGN", "SOUNDEX", "SUBSTR", "SUM", "TIME",
        "TOTAL", "TRIM", "TYPEOF", "UNICODE", "UPPER", "ZEROBLOB",
        "CAST", "CASE", "WHEN", "THEN", "ELSE", "END", "EXISTS", "ALL", "ANY", "IN", '`', "\"","||","SLEEP","*","/"
    ]
    conn = ""
    cursor = ""
    blacklist = ""
    sensitive_blacklist = ""

    def __init__(self,black_list:list=[],sensitive_blacklist=False):
        """
        Parameters:
            black_list (list): a list of strings that shouldn't be in the user supplied data
            sensitive_blacklist (bool): to check whether your the check should be case sensitive or not, True for sensitibe and false for insensitve default is insensetive 
        """
        import sqlite3
        self.conn = sqlite3.connect('./flag.db',check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.sensitive_blacklist = sensitive_blacklist
        if not sensitive_blacklist:
            from itertools import product
            self.black_list = [''.join(c) for word in black_list for c in product(*[(ch.lower(), ch.upper()) for ch in word])]
        else:
            self.blacklist = black_list

    def setup(self,queries:list):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS dict (word TEXT COLLATE NOCASE unique, meaning TEXT)")
        for query in queries:
            try:
                self.cursor.execute(query)
            except:
                pass
        self.conn.commit()

    def prepare_query(self,query, data):
        if not isinstance(data, str):
            data = " ".join(data)
        query = query.replace("?",f"'{data}'")
        return query
    
    def query(self,prepared_query,data):
        if self.blacklist_check(data):
            data = self.security_check(data)
            if data:
                query = self.prepare_query(prepared_query,data)
                result = self.cursor.execute(query).fetchone()
                return result[0] if result else "None"
            else:
                raise ValueError("Security Violation")
        else:
            raise ValueError("Security Violation")
         
    def security_check(self,data):
        """Checks if any SQL keyword appeared in the user provided data"""
        if not isinstance(data,str):
            data = " ".join(data)
        data = data.upper()
        if any(term in data for term in self.sql_terms):
            return False
        else:
            return data
    
    def blacklist_check(self,data):
        """Checks if any word of the blacklist exists in the user provided data"""
        if any(bad in item for bad in self.black_list for item in data):
            return False
        return True

    def __del__(self):
        self.conn.close()