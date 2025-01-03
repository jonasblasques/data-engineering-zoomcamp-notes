## Module 2 Homework

### Assignment


1) Within the execution for `Yellow` Taxi data for the year `2020` and month `12`: what is the uncompressed file size (i.e. the output file `yellow_tripdata_2020-12.csv` of the `extract` task)?
- 128.3 MB
- 134.5 MB
- 364.7 MB
- 692.6 MB

Answer: Output --> Extract --> Outputfiles --> 128,3 mb

2) What is the task run state of tasks bq_green_tripdata, bq_green_tmp_table and bq_merge_green when you run the flow with the `taxi` input set to value `yellow`?
- `SUCCESS`
- `FAILED`
- `SKIPPED`
- `CANCELED`

Answer: `SKIPPED`

3) How do we deal with table schema in the Google Cloud ingestion pipeline?
- We don't define the schema at all because this is a data lake after all
- We let BigQuery autodetect the schema
- Kestra automatically infers the schema from the extracted data
- We explicitly define the schema in the tasks that create external source tables and final target tables

Answer: We explicitly define the schema

4) How does Kestra handles backfills in the scheduled flow?
- You need to define backfill properties in the flow configuration
- You have to run CLI commands to backfill the data
- You can run backfills directly from the UI from the Flow Triggers tab by selecting the time period
- Kestra doesn't support backfills

Answer: You can run backfills directly from the UI from the Flow Triggers

5) Which of the following CRON expressions schedules a flow to run at 09:00 UTC on the first day of every month?
- `0 9 1 * *`
- `0 1 9 * *`
- `0 9 * * *`
- `1 9 * * *`

Answer: `0 9 1 * *`

6) How would you configure the timezone to New York in a Schedule trigger?
- Add a `timezone` property set to `EST` in the `Schedule` trigger configuration  
- Add a `timezone` property set to `America/New_York` in the `Schedule` trigger configuration
- Add a `timezone` property set to `UTC-5` in the `Schedule` trigger configuration
- Add a `location` property set to `New_York` in the `Schedule` trigger configuration  

 Kestra uses the IANA time zone database for specifying time zones, and for New York, the timezone is "America/New_York"

 Answer: Add a `timezone` property set to `America/New_York` in the `Schedule` trigger configuration


## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2025/homework/hw2
* Check the link above to see the due date