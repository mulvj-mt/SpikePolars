"""Reads a whole csv file to memory and writes to parquet in S3."""
import logging
import os
import time
import polars as pl
import boto3
from botocore.exceptions import ClientError
import json
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s %(funcName)s:%(lineno)d - %(message)s'
    )

DATA_DESTINATION_PREFIX = os.environ["DATA_DESTINATION_PREFIX"]
DATA_BUCKET = os.environ["DATA_BUCKET"]

storage_options = {"aws_region": "eu-west-2"}

s3 = boto3.client('s3')

def get_schema(path_to_schema_file:str) -> pl.Schema | None:
    logger.info(f"Getting schema from {path_to_schema_file}")
    try:
        response = s3.get_object(Bucket=DATA_BUCKET, Key=path_to_schema_file)
        schema = json.loads(response['Body'].read().decode('utf-8'))
        schema_def = {k:pl.String() if v == 'string' else pl.Int64() for k, v in schema.items()}
        return pl.Schema(schema_def)
    except ClientError as c:
        logger.error(f'Error getting schema from {path_to_schema_file}: {c}')


def etl(data_source: str, schema_source: str) -> dict:
    logger.info('Starting execution')
    start = time.time()
    try:
        logger.info('Getting schema')
        schema = get_schema(schema_source)
        logger.info(f'Reading {data_source}')
        df = scan_csv_source(data_source, schema)
        cleaned = clean_df(df)
        output_path = get_output_path(data_source)
        logger.info(f'Writing {output_path}')
        result = write_to_parquet(cleaned, output_path)
        return result
    except pl.exceptions.PolarsError as p:
        logger.error('Execution interrupted because of a Polars Error')
        return {"statusCode": 500, "body": str(p)}
    except Exception as e:
        logger.error(f'An unexpected error occurred: {e}')
        logger.error(f'Traceback: {traceback.format_exc()}')
        return {"statusCode": 500, "body": str(e)}
    finally:
        end = time.time()
        logger.info(f'Execution took {end - start} seconds')


def clean_df(df: pl.LazyFrame) -> pl.LazyFrame:
    new_df = df.filter(pl.col("id") == -1)
    logger.info(f'There are {len(new_df.collect())} rows where id = -1')
    return df


def scan_csv_source(source_path: str, schema: pl.Schema) -> pl.LazyFrame:
    """Reads a CSV file into a Polars Lazyframe."""
    try:
        df = pl.scan_csv(source_path, infer_schema_length=0, separator='|', schema=schema)
        logger.info(f"Successfully read CSV from: {source_path}")
        return df
    except pl.exceptions.PolarsError as p:
        logger.error(f'Error reading CSV from: {source_path}')
        logger.error(f'There was a Polars error: {p}')
        raise p


def write_to_parquet(df: pl.LazyFrame, output_path: str) -> dict:
    """Writes a Polars Dataframe to parquet."""
    try:
        logger.info('Commencing write...')
        df.sink_parquet(output_path, compression='snappy', row_group_size=10000, storage_options=storage_options)
        logger.info(f"Successfully written DataFrame to Parquet: {output_path}")
        return {"statusCode": 200, "body": output_path}
    except pl.exceptions.PolarsError as p:
        logger.error(f'Error writing DataFrame to Parquet: {output_path}')
        logger.error(f'There was a Polars error: {p}')
        raise p


def get_output_path(input_source: str) -> str:
    filename = input_source.split('/')[-1]
    stem = filename.split('.')[0]
    return f"s3://{DATA_BUCKET}/{DATA_DESTINATION_PREFIX}/{stem}.parquet"


if __name__ == '__main__':
    data_source = f"s3://{DATA_BUCKET}/source/fake_data.csv"
    schema_source = "schema/schema.json"
    listing = s3.list_objects(Bucket=DATA_BUCKET)
    logger.info(f'Found {len(listing)} objects in {DATA_BUCKET}')
    etl(data_source, schema_source)