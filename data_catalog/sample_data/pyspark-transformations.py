from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, round

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("PySparkSQLDataTransformation") \
    .getOrCreate()

# Sample data
data = [
    ("Alice", 30, "New York"),
    ("Bob", 25, "Los Angeles"),
    ("Charlie", 35, "New York"),
    ("David", 28, "Chicago"),
    ("Eve", 30, "Los Angeles")
]
columns = ["Name", "Age", "City"]
df = spark.createDataFrame(data, columns)

print("Original DataFrame:")
df.show()

# --- Data Transformation using DataFrame API ---

# 1. Add a new column 'Age_Category' based on 'Age'
df_transformed_api = df.withColumn(
    "Age_Category",
    when(col("Age") < 30, "Young").otherwise("Adult")
)

# 2. Filter rows where City is 'New York'
df_filtered_api = df_transformed_api.filter(col("City") == "New York")

# 3. Calculate average age per city
df_agg_api = df_filtered_api.groupBy("City").agg(
    round(avg("Age"), 2).alias("Average_Age")
)

print("\nTransformed DataFrame (DataFrame API):")
df_agg_api.show()

# --- Data Transformation using Spark SQL ---

# Register the DataFrame as a temporary view
df.createOrReplaceTempView("people")

# 1. Add a new column 'Age_Category' and filter based on 'City' using SQL
sql_query_filtered = """
SELECT
    Name,
    Age,
    City,
    CASE
        WHEN Age < 30 THEN 'Young'
        ELSE 'Adult'
    END AS Age_Category
FROM
    people
WHERE
    City = 'New York'
"""
df_filtered_sql = spark.sql(sql_query_filtered)

# 2. Calculate average age per city using SQL
sql_query_agg = """
SELECT
    City,
    ROUND(AVG(Age), 2) AS Average_Age
FROM
    (
        SELECT
            Name,
            Age,
            City,
            CASE
                WHEN Age < 30 THEN 'Young'
                ELSE 'Adult'
            END AS Age_Category
        FROM
            people
        WHERE
            City = 'New York'
    ) AS filtered_people
GROUP BY
    City
"""
df_agg_sql = spark.sql(sql_query_agg)

print("\nTransformed DataFrame (Spark SQL):")
df_agg_sql.show()

# Stop the SparkSession
spark.stop()
