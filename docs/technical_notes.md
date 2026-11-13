# Technical choices and encountered problems

- **Actual broker:** a native Apache Kafka 3.9.1 KRaft broker was run with Java 17.
  Docker configuration is an alternative; Docker was not installed on the test machine.
- **Spaces in the project path:** Kafka's shell startup expanded JVM logging arguments
  containing `Data Collect` incorrectly and failed to find its main class. The launcher now
  calls Java with an argument list, so project paths with spaces are supported.
- **IPv4/IPv6:** the broker binds to IPv4 loopback. Using `localhost` in Python first attempted
  IPv6 and logged failed attempts before falling back to IPv4. The advertised/default client
  address is explicitly `127.0.0.1` to avoid these misleading connection errors.
- **Raw data had no validation failures:** counts are reported honestly as zero invalid rows.
  Four clearly separated test records demonstrate detection without contaminating the database.
- **Original data had no missing means or duplicate city/date rows:** their absence is measured.
  Isolated unit tests exercise optional-mean imputation and duplicate removal.
- **Finite stream:** one partition preserves order; run_id separates reruns, an expected-count
  termination condition avoids an endless Consumer, and content hashing detects missing/changed data.
- **No model training:** the assignment evaluates collection and preparation. Extra analysis
  compares weather exposure and within-month deviations; it does not make unsupported forecasts.
- **Repeated Kafka runs and response limits:** kafka-python's default maximum response frame
  is smaller than its default partition fetch size. Once the topic accumulated several runs,
  a fetch logged InvalidReceiveError and retried. The Consumer now explicitly allows an 8 MiB
  response with a 4 MiB fetch / 2 MiB partition fetch, leaving space for protocol overhead.
- **Scope:** single local broker, small finite dataset, no production availability guarantee.
  Exactly-once processing across distributed failures is not claimed. Database loading of an
  identical dataset is idempotent, and failed/partial Kafka runs must be retried explicitly.
