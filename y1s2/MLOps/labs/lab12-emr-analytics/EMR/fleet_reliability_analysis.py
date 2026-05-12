from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import argparse


def transform_data(data_source: str, output_uri: str) -> None:
    with SparkSession.builder.appName("Maintenance Event Aggregation").getOrCreate() as spark:
        spark.conf.set("spark.sql.shuffle.partitions", "8")

        df = spark.read.option("header", "true").csv(data_source)

        df = df.withColumn("downtime_hours", col("downtime_hours").cast("double")) \
               .withColumn("labor_hours", col("labor_hours").cast("double")) \
               .withColumn("parts_cost_usd", col("parts_cost_usd").cast("double")) \
               .withColumn("total_cost_usd", col("total_cost_usd").cast("double"))

        df.createOrReplaceTempView("maintenance_events")

        AGGREGATION_QUERY = """
            SELECT
                aircraft_id,
                ata_chapter,
                ata_system_name,
                COUNT(*)                            AS critical_event_count,
                ROUND(SUM(downtime_hours), 1)       AS total_downtime_hrs,
                ROUND(AVG(downtime_hours), 1)       AS avg_downtime_hrs,
                ROUND(SUM(labor_hours), 1)          AS total_labor_hrs,
                ROUND(SUM(total_cost_usd), 2)       AS total_cost,
                ROUND(AVG(total_cost_usd), 2)       AS avg_cost_per_event
            FROM maintenance_events
            WHERE event_type IN ('UNSCHEDULED', 'AOG')
              AND severity IN ('CRITICAL', 'MAJOR')
            GROUP BY aircraft_id, ata_chapter, ata_system_name
        """

        transformed_df = spark.sql(AGGREGATION_QUERY)

        transformed_df.write.mode("overwrite").parquet(output_uri)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Maintenance Event Aggregation — EMR Spark Job")
    parser.add_argument("--data_source", required=True,
                        help="S3 URI to maintenance_events.csv")
    parser.add_argument("--output_uri", required=True,
                        help="S3 URI for Parquet output")
    args = parser.parse_args()

    transform_data(args.data_source, args.output_uri)
