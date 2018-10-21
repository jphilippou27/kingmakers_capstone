import time
import datetime
import pyspark
from pyspark.sql.types import StringType, IntegerType, StructType, StructField, FloatType, BooleanType, DateType

def now():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')

class Schema(object):
    
    @classmethod
    def __init__(self, schema_str):
        self.column_names = None
        self._initialized = False
        self._column_dt_formats = {}
        
        self._schema_str = schema_str
        self.process_schema()
    
    @classmethod
    def _check_init(self):
        if not self._initialized:
            raise Exception('Schema not initialized')
    
    @staticmethod
    def spark_dtype(col_info):
        dtype = col_info
        if hasattr(col_info, '__get__'):
            dtype = col_info['dataType']

        if Schema._is_text_datatype(dtype):
            return StringType()
        elif Schema._is_integer_datatype(dtype):
            return IntegerType()
        elif Schema._is_float_datatype(dtype):
            return FloatType()
        elif Schema._is_bool_datatype(dtype):
            return BooleanType()
        elif Schema._is_datetime_datatype(dtype):
            return DateType()
        else:
            raise Exception(f'Unknown datatype: {dtype}')
    
    @staticmethod
    def pandas_dtype(col_info):
        dtype = col_info
        if hasattr(col_info, '__get__'):
            dtype = col_info['dataType']

        if Schema._is_text_datatype(dtype):
            return 'str'
        elif Schema._is_integer_datatype(dtype):
            return 'int'
        elif Schema._is_float_datatype(dtype):
            return 'float'
        elif Schema._is_bool_datatype(dtype):
            return 'bool'
        elif Schema._is_datetime_datatype(dtype):
            return 'str'  # Pandas doesn't care about datetimes in the schema string, you have to tell it about them separately.
        else:
            raise Exception(f'Unknown datatype: {dtype}')
            
    @staticmethod
    def hive_dtype(col_info):
        dtype = col_info
        if hasattr(col_info, '__get__'):
            dtype = col_info['dataType']

        if Schema._is_text_datatype(dtype):
            return 'STRING'
        elif Schema._is_integer_datatype(dtype):
            return 'INTEGER'
        elif Schema._is_float_datatype(dtype):
            return 'DOUBLE'
        elif Schema._is_bool_datatype(dtype):
            return 'BOOLEAN'
        elif Schema._is_datetime_datatype(dtype):
            return 'DATE'
        else:
            raise Exception(f'Unknown datatype: {dtype}')
    
    @classmethod
    def process_schema(self):
        if self._initialized:
            raise Exception('Schema already initialized')
        
        self.parsed_schema = [{
            'name': self.add_name(name),
            'description': description,
            'dataType': dataType,
            'source': source,
            'sparkDtype': Schema.spark_dtype(dataType),
            'pandasDtype': Schema.pandas_dtype(dataType),
            'hiveDtype': Schema.hive_dtype(dataType)
        } for (name, description, dataType, source) in map(lambda c: c.split('\n'), self._schema_str)]
        
        self._initialized = True
    
    @classmethod
    def add_name(self, col_name):
        if self.column_names is None:
            self.column_names = [col_name]
        else:
            self.column_names.append(col_name)
        return col_name
    
    @classmethod
    def register_column_datetime_formats(self, formats):
        if formats:
            for col, fmt in formats.items():
                self._column_dt_formats[col] = fmt
        
    @classmethod
    def get_pandas_schema(self):
        self._check_init()
        return { col['name']: col['pandasDtype'] for col in self.parsed_schema }
    
    @classmethod
    def get_spark_dtypes(self):
        self._check_init()
        return StructType([ StructField(col['name'], col['sparkDtype'], True) for col in self.parsed_schema ])
    
    @classmethod
    def get_dt_colnames(self):
        self._check_init()
        return list(filter(lambda c: Schema._is_datetime_datatype(c['dataType']), self.parsed_schema))
    
    @classmethod
    def hive_ddl(self, tableName, externalTableLocation, external=True, csv_quotechar='|', csv_delimiter=','):
        self._check_init()
        columnData = []
        for c in self.parsed_schema:
            columnStr = "`{}` {} COMMENT '{}, orig-datatype {}, source {}'".format(c['name'],
                                                                                 c['hiveDtype'],
                                                                                 c['description'].replace("'", "").replace('"', ''),
                                                                                 c['dataType'].replace("'", "").replace('"', ''),
                                                                                 c['source'].replace("'", "").replace('"', ''))
            columnData.append(columnStr)
        
        ddl = """
DROP TABLE IF EXISTS {tableName};
        
CREATE{isExternal} TABLE {tableName}
(
    {columnPart}
)
COMMENT 'Auto-generated schema at {now} from {externalTableLocation}'
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = "{csv_delimiter}",
   "quoteChar"     = "{csv_quotechar}"
)
STORED AS TEXTFILE
LOCATION '{externalTableLocation}';

""".format(isExternal=' EXTERNAL' if external else '',
           tableName=tableName,
           columnPart=',\n    '.join(columnData),
           now=now(),
           csv_delimiter=csv_delimiter,
           csv_quotechar=csv_quotechar,
           externalTableLocation=externalTableLocation)
        return ddl
    
    @classmethod
    def hive_ddl_parquet(self, tableName, originalTableName):
        """
        Create a new table by selecting data out of an existing (external) table and inserting
        into a parquet table managed by Hive.
        """
        self._check_init()
        selectData = []
        alterTableStmtsList = []
        for c in self.parsed_schema:
            dtype = c['hiveDtype']
            if dtype == 'STRING':
                columnStr = "`{name}` AS `{name}`".format(name=c['name'])
            elif dtype == 'INTEGER':
                columnStr = "CAST(`{name}` AS {dtype}) AS `{name}`".format(name=c['name'], dtype=dtype)
            elif dtype == 'DOUBLE':
                columnStr = "CAST(`{name}` AS {dtype}) AS `{name}`".format(name=c['name'], dtype=dtype)
            elif dtype == 'BOOLEAN':
                columnStr = "CAST(`{name}` AS {dtype}) AS `{name}`".format(name=c['name'], dtype=dtype)
            elif dtype == 'DATE':
                columnStr = "TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(`{name}`, '{dtConvStr}'))) AS `{name}`".format(name=c['name'],
                                                                                            dtConvStr=self._column_dt_formats[c['name']])
            
            comment = c['description'].replace("'", "").replace('"', '')
            comment += ', orig-dtype=' + c['dataType'].replace("'", "").replace('"', '')
            comment += ', source=' + c['source'].replace("'", "").replace('"', '')
            alterTableStmt = "ALTER TABLE {tableName} CHANGE `{name}` `{name}` {dtype} COMMENT '{comment}';".format(tableName=tableName,
                                                                                                                    name=c['name'],
                                                                                                                    dtype=dtype,
                                                                                                                    comment=comment)
            
            selectData.append(columnStr)
            alterTableStmtsList.append(alterTableStmt)
            
        ddl = """
DROP TABLE IF EXISTS {tableName};
        
CREATE TABLE {tableName} 
COMMENT 'Auto-generated schema at {now} from {originalTableName}' 
STORED AS PARQUET 
AS SELECT
    {selectStatement}
FROM {originalTableName};

{alterTableStmts}
""".format(tableName=tableName,
           originalTableName=originalTableName,
           selectStatement=',\n    '.join(selectData),
           now=now(),
           alterTableStmts='\n'.join(alterTableStmtsList)
           )
        return ddl

    @classmethod
    def hive_ddl_parquet_select(self, tableName, originalTableName):
        """
        Return only the "SELECT ..." clause portion from the CTAS statement in `hive_ddl_parquet' 
        """
        self._check_init()
        selectData = []
        for c in self.parsed_schema:
            dtype = c['hiveDtype']
            if dtype == 'STRING':
                columnStr = "`{name}` AS `{name}`".format(name=c['name'])
            elif dtype == 'INTEGER':
                columnStr = "CAST(`{name}` AS {dtype}) AS `{name}`".format(name=c['name'], dtype=dtype)
            elif dtype == 'DOUBLE':
                columnStr = "CAST(`{name}` AS {dtype}) AS `{name}`".format(name=c['name'], dtype=dtype)
            elif dtype == 'BOOLEAN':
                columnStr = "CAST(`{name}` AS {dtype}) AS `{name}`".format(name=c['name'], dtype=dtype)
            elif dtype == 'DATE':
                columnStr = "TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(`{name}`, '{dtConvStr}'))) AS `{name}`".format(name=c['name'],
                                                                                            dtConvStr=self._column_dt_formats[c['name']])
            
            comment = c['description'].replace("'", "").replace('"', '')
            
            
            selectData.append(columnStr)
            
        selStmt = """SELECT
    {selectStatement}
FROM {originalTableName}
""".format(originalTableName=originalTableName,
           selectStatement=',\n    '.join(selectData),
           )
        return selStmt
    
    @classmethod
    def hive_ddl_parquet_alter(self, tableName, originalTableName):
        """
        Return only the ALTER TABLE statements from the `hive_ddl_parquet' DDL 
        """
        self._check_init()
        alterTableStmtsList = []
        for c in self.parsed_schema:
            dtype = c['hiveDtype']
            comment = c['description'].replace("'", "").replace('"', '')
            comment += ', orig-dtype=' + c['dataType'].replace("'", "").replace('"', '')
            comment += ', source=' + c['source'].replace("'", "").replace('"', '')
            alterTableStmt = "ALTER TABLE {tableName} CHANGE `{name}` `{name}` {dtype} COMMENT '{comment}';".format(tableName=tableName,
                                                                                                                    name=c['name'],
                                                                                                                    dtype=dtype,
                                                                                                                    comment=comment)
            
            alterTableStmtsList.append(alterTableStmt)
            
        alterTableStmts='\n'.join(alterTableStmtsList)
        return alterTableStmts
    
    
    @staticmethod
    def _is_text_datatype(dtype):
        return dtype.lower().startswith('text')
    
    @staticmethod
    def _is_integer_datatype(dtype):
        return dtype.lower().startswith('integer')

    @staticmethod
    def _is_float_datatype(dtype):
        if 'precision' in dtype.lower():
            return True
        elif 'float' in dtype.lower():
            return True
        return False

    @staticmethod
    def _is_bool_datatype(dtype):
        return dtype.lower().startswith('bit')

    @staticmethod
    def _is_datetime_datatype(dtype):
        if 'mm/dd/yyyy' in dtype.lower():
            return True
        elif 'date' in dtype.lower():
            return True
        elif 'yyyy-MM-dd' in dtype.lower():
            return True
        elif 'yyyy' in dtype.lower():
            return True  # probably, right?
        return False