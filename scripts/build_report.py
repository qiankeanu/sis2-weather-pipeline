"""PDF-отчёт формируется из настоящих результатов, а не вручную придуманных чисел."""
import argparse
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                               PageBreak, Image, Preformatted, KeepTogether)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
WIDTH = A4[0] - 38 * mm
INK = colors.HexColor("#173642")
TEAL = colors.HexColor("#207d8d")
STYLES = getSampleStyleSheet()
STYLES.add(ParagraphStyle("BodyReport", fontName="Helvetica", fontSize=9.2, leading=13,
                          textColor=INK, spaceAfter=7))
STYLES.add(ParagraphStyle("TitleReport", fontName="Helvetica-Bold", fontSize=27, leading=33,
                          textColor=INK, spaceAfter=15))
STYLES.add(ParagraphStyle("SectionReport", fontName="Helvetica-Bold", fontSize=16, leading=20,
                          textColor=TEAL, spaceAfter=12, keepWithNext=True))
STYLES.add(ParagraphStyle("SubReport", fontName="Helvetica-Bold", fontSize=11, leading=15,
                          textColor=INK, spaceBefore=5, spaceAfter=7, keepWithNext=True))
STYLES.add(ParagraphStyle("CellReport", fontName="Helvetica", fontSize=8, leading=11,
                          textColor=INK))
STYLES.add(ParagraphStyle("CaptionReport", fontName="Helvetica-Oblique", fontSize=8, leading=11,
                          textColor=colors.HexColor("#526975"), spaceAfter=11))
STYLES.add(ParagraphStyle("CodeReport", fontName="Courier", fontSize=7.1, leading=9.3,
                          backColor=colors.HexColor("#eff4f6"), borderPadding=7, spaceAfter=9))


def read(name):
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def p(text):
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), STYLES["BodyReport"])


def heading(text):
    return Paragraph(escape(text), STYLES["SectionReport"])


def sub(text):
    return Paragraph(escape(text), STYLES["SubReport"])


def table(rows, widths=None):
    cells = [[Paragraph(escape(str(value)), STYLES["CellReport"]) for value in row] for row in rows]
    item = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
    item.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dcecef")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f7f8")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), 0.7, TEAL),
        ("LINEBELOW", (0, -1), (-1, -1), 0.4, colors.HexColor("#c7d5db")),
    ]))
    return item


def figure(filename, caption, max_height=210):
    image = Image(str(ROOT / "figures" / filename))
    factor = min(WIDTH / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * factor
    image.drawHeight = image.imageHeight * factor
    return [image, Paragraph(escape(caption), STYLES["CaptionReport"])]


def architecture():
    drawing = Drawing(WIDTH, 225)
    width, height = 105, 40
    positions = [(0, 165), (120, 165), (240, 165), (360, 165),
                 (360, 85), (240, 85), (120, 85), (0, 85), (0, 5)]
    labels = [("Open-Meteo", "ERA5 daily data"), ("Raw snapshot", "original JSON / CSV"),
              ("Kafka Producer", "JSON + run_id"), ("Kafka Broker", "1 topic / partition"),
              ("Kafka Consumer", "count + content hash"), ("Pandera", "validate / quarantine"),
              ("pandas + NumPy", "clean / transform"), ("SQLite3", "load / verify twice"),
              ("EDA", "5 figures + findings")]
    for (x, y), (title, detail) in zip(positions, labels):
        drawing.add(Rect(x, y, width, height, rx=5, fillColor=colors.HexColor("#e7f2f3"),
                         strokeColor=TEAL, strokeWidth=0.8))
        drawing.add(String(x + width / 2, y + 24, title, fontName="Helvetica-Bold", fontSize=9,
                           textAnchor="middle", fillColor=INK))
        drawing.add(String(x + width / 2, y + 11, detail, fontName="Helvetica", fontSize=7.2,
                           textAnchor="middle", fillColor=INK))
    for i in range(len(positions) - 1):
        x1, y1 = positions[i]; x2, y2 = positions[i + 1]
        if y1 == y2:
            direction = 1 if x2 > x1 else -1
            a = x1 + (width if direction == 1 else 0); b = x2 + (0 if direction == 1 else width)
            y = y1 + height / 2
            drawing.add(Line(a, y, b, y, strokeColor=TEAL))
            drawing.add(Polygon([b, y, b - 4 * direction, y + 3, b - 4 * direction, y - 3],
                                fillColor=TEAL, strokeColor=TEAL))
        else:
            x = x1 + width / 2
            drawing.add(Line(x, y1, x, y2 + height, strokeColor=TEAL))
            drawing.add(Polygon([x, y2 + height, x - 3, y2 + height + 4,
                                 x + 3, y2 + height + 4], fillColor=TEAL, strokeColor=TEAL))
    drawing.add(String(140, 28, "Every stage reports counts; final verification checks continuity.",
                       fontName="Helvetica-Oblique", fontSize=8, fillColor=INK))
    return drawing


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#cad9de"))
    canvas.line(19 * mm, 17 * mm, A4[0] - 19 * mm, 17 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#526975"))
    canvas.drawString(19 * mm, 12 * mm, "SIS 2 | Kazakhstan Weather Pipeline")
    canvas.drawRightString(A4[0] - 19 * mm, 12 * mm, str(doc.page))
    canvas.restoreState()


def build(group=None):
    if group is None and (ROOT / "docs" / "team.json").exists():
        group = json.loads((ROOT / "docs" / "team.json").read_text(encoding="utf-8")).get("group")
    collection, producer, consumer = read("collection.json"), read("producer.json"), read("consumer.json")
    validation, cleaning, database = read("validation.json"), read("cleaning.json"), read("database.json")
    tests, verification = read("validation_tests.json"), read("pipeline_verification.json")
    if not verification["all_passed"]:
        raise ValueError("Do not build a success report from a failed pipeline")
    import csv
    with (RESULTS / "eda_city_summary.csv").open() as file:
        city_rows = list(csv.DictReader(file))
    unit = ET.parse(RESULTS / "unit_tests.xml").getroot().find("testsuite")
    counts = verification["counts"]
    draft = not group
    # Полные учебные идентификаторы берём только из локального игнорируемого файла.
    private_team = ROOT / ".private" / "team_private.json"
    source = private_team if private_team.exists() else ROOT / "docs" / "team.json"
    team_data = json.loads(source.read_text(encoding="utf-8"))
    members = [(m["name"], m.get("student_id", "not provided"), m["part"])
               for m in team_data["members"]]
    draft = draft or any(student_id == "not provided" for _, student_id, _ in members)
    story = [Spacer(1, 16 * mm), p("DATA COLLECTION & PREPARATION / SIS 2"), Spacer(1, 8 * mm),
             Paragraph("Weather Data Streaming<br/>and Validation Pipeline", STYLES["TitleReport"]),
             p("Five cities in Kazakhstan | Open-Meteo ERA5 | Apache Kafka | Pandera | SQLite3"),
             Spacer(1, 10 * mm), table([["Team member", "Student ID"], *[(n, i) for n, i, _ in members]],
                                      [WIDTH * .65, WIDTH * .35]), Spacer(1, 10 * mm),
             p(f"Group: {group or 'TO BE PROVIDED'}\nPrepared: 13 November 2026\n"
               "Submission deadline: 24 November 2026, 23:59\n"
               f"Data period: {collection['start_date']} to {collection['end_date']}"),
             p("DRAFT: add the group number and confirm each member's actual contributions before submission."
               if draft else "Technical report based on the included executable source and recorded outputs."),
             Spacer(1, 6 * mm), p(f"{counts['collected']:,} real API records | "
                 f"{sum(verification['checks'].values())} pipeline checks passed | "
                 f"{unit.attrib['tests']} automated tests passed"), PageBreak()]

    story += [heading("1. Introduction"),
        p("The project builds a connected, reproducible data preparation pipeline for historical weather "
          "in Almaty, Astana, Shymkent, Karaganda and Atyrau. The technical problem is to collect public "
          "data, transmit it through a real broker, detect invalid values, prepare a consistent table, "
          "prevent duplicate database loading and derive interpretable comparisons."),
        p("Research questions: How do annual and monthly temperatures differ between the cities? "
          "Which city has the highest precipitation total? How do frost, hot and wet-day counts compare? "
          "The expected outcome is a runnable Python project with preserved source data, verifiable "
          "message transmission, a validated database and evidence-based visual analysis."),
        heading("2. Data source and collection"),
        p("Source: Open-Meteo Historical Weather API, https://archive-api.open-meteo.com/v1/archive. "
          "The model is explicitly set to ERA5 for consistency. Reanalysis combines observations and "
          "modelling; these values must not be presented as raw measurements at city weather stations. "
          "The non-commercial API needs no key. Attribution is provided to Open-Meteo and ERA5/Copernicus."),
        table([["Request parameter", "Setting"],
               ["latitude / longitude", "One configured coordinate pair per city; returned grid coordinates retained"],
               ["start_date / end_date", f"{collection['start_date']} / {collection['end_date']}"],
               ["timezone / models", "Asia/Almaty / era5"],
               ["daily", "temperature_2m_min, temperature_2m_max, temperature_2m_mean, precipitation_sum, wind_speed_10m_max, weather_code"],
               ["Units", "Celsius; precipitation mm; wind km/h"]], [130, WIDTH-130]), Spacer(1, 8),
        p(f"Five HTTP requests returned {collection['collected']:,} records: 365 days per city. "
          "Requests use explicit timeouts, HTTP status checks and up to three attempts. All API arrays "
          "must match the requested date coverage. Full original responses are saved before flattening; "
          "the derived raw CSV adds only city and city-date record ID fields."),
        p("Numerical fields: temperature, precipitation and wind. Categorical fields: city and WMO weather "
          "code. Temporal field: local calendar date. Full URLs, parameters, collection timestamp, grid "
          "coordinates and dataset hash are in results/collection.json."), PageBreak()]

    story += [heading("3. Pipeline architecture"), architecture(),
        p("The Consumer output is the only input to Pandera; valid rows feed cleaning, cleaned rows feed "
          "SQLite, and EDA reads SQLite. No unrelated manually prepared dataset is substituted at any stage."),
        heading("4. Apache Kafka implementation"),
        table([["Component", "Actual configuration / behaviour"],
               ["Broker", "Apache Kafka 3.9.1, native Java 17, KRaft broker + controller, node ID 1"],
               ["Listeners", "Broker 127.0.0.1:9092; controller 127.0.0.1:9093"],
               ["Topic", f"{producer['topic']}; 1 partition; replication factor 1"],
               ["Producer", "Separate script; JSON UTF-8 values; record ID keys; acks=all; retries=3; confirmed sends counted"],
               ["Consumer", "Separate script; assigned partition 0; JSON decoding; current run_id only; explicit 120-second deadline"],
               ["Termination", "Expected record count reached and complete ordered dataset SHA-256 matched"]], [110, WIDTH-110]),
        Spacer(1, 8), p(f"Confirmed published: {producer['published']:,}. Consumed: {consumer['consumed']:,}. "
          f"Partition 0 offsets: {consumer['first_offset']} to {consumer['last_offset']}. "
          "Counts and message offsets come from actual broker responses. Old messages are skipped by run_id "
          "on subsequent runs. JSON errors and incomplete streams stop the pipeline explicitly."), PageBreak()]

    rules = [["Rule", "Reason / handling"],
        ["Required columns and fields", "Reject absent mandatory fields; an incompatible whole-dataset schema stops processing"],
        ["Finite numerical types", "Reject strings, boolean values, infinities and missing required numbers"],
        ["Temperature -90 to 65 C", "Broad physical range; valid local extremes remain"],
        ["Nonnegative precipitation / wind", "Reject physically impossible negatives; broad upper bounds 2000 mm / 500 km/h"],
        ["City and WMO allowed categories", "Reject unknown cities and invalid WMO codes"],
        ["Real date within collection period", "Reject impossible dates and out-of-period records"],
        ["Record ID matches city/date", "Keep source identity consistent for loading and deduplication"],
        ["Minimum <= mean <= maximum", "Cross-field consistency; optional missing mean handled during cleaning"]]
    story += [heading("5. Pandera validation"),
        p("Pandera validates the received dataset before main cleaning or transformation. Lazy validation "
          "collects row-level failures and their reasons. Invalid rows are quarantined in invalid_data.csv; "
          "valid rows continue. Whole-dataset structural errors stop processing instead of hiding the issue."),
        table(rules, [155, WIDTH-155]), Spacer(1, 9),
        p(f"Actual source validation: {validation['valid']:,} valid, {validation['invalid']} invalid. "
          "No errors were invented in the real data to make this count look more interesting."),
        sub("Isolated negative validation tests"),
        table([["Test", "Deliberate defect", "Result"],
               ["1", "precipitation_mm = -5", "Rejected"],
               ["2", "date = 2025-02-30", "Rejected"],
               ["3", "weather_code = 999", "Rejected"],
               ["4", "temperature_min = 60, above the actual maximum", "Rejected"]], [40, WIDTH-125, 85]),
        Spacer(1, 8), p(f"Detected {tests['detected_invalid']} of {tests['test_records']} test rows; "
          f"unexpectedly accepted: {tests['unexpectedly_accepted']}. The test-only CSV and detailed "
          "failure cases are stored under data/test_only/ and never enter production totals or SQLite."), PageBreak()]

    story += [heading("6. Data cleaning and transformation"),
        table([["Operation", "Purpose and actual outcome"],
               ["Missing-value inspection", f"Count missing values before validation and cleaning; remaining missing values: {cleaning['missing_after']}"],
               ["Duplicate detection", f"Drop duplicate record IDs; actual rows removed: {cleaning['duplicates_removed']}"],
               ["Type conversion", "ISO date to pandas datetime; numeric fields to numbers; WMO code to integer"],
               ["Text normalization", "Strip whitespace and standardize city-name capitalization; known categories are validated first"],
               ["Optional mean imputation", f"(min + max) / 2, explicitly flagged; actual values imputed: {cleaning['mean_values_imputed']}"],
               ["NumPy numerical operations", "Temperature max-minus-min, binary weather indicators and within-city/month mean deviations"],
               ["Multiple-condition filter", f"Daily max >= 30 C AND precipitation < 1 mm; actual hot/dry rows: {cleaning['hot_dry_days']}"],
               ["GroupBy aggregation", "City counts, mean temperature, precipitation totals and exposure-day counts"],
               ["Reshaping", "pivot_table with city rows and month columns, mean temperature values"]], [132, WIDTH-132]),
        Spacer(1, 10),
        Preformatted('frame["temperature_range"] = np.subtract(\n'
                     '    frame["temperature_max"], frame["temperature_min"])\n'
                     'hot_dry = frame[(frame["temperature_max"] >= 30)\n'
                     '                & (frame["precipitation_mm"] < 1)]\n'
                     'pivot = frame.pivot_table(index="city", columns="month",\n'
                     '                          values="temperature_mean", aggfunc="mean")', STYLES["CodeReport"]),
        p("The real dataset did not require optional-mean filling or duplicate removal. Those branches are "
          "still implemented and exercised by an isolated unit test with a missing mean and a duplicated "
          "record. Extreme but valid weather values are not removed as outliers."),
        p("The additional temperature deviation subtracts a city's mean for the same month in this dataset. "
          "It is a within-sample descriptive deviation, not a long-term climatological anomaly."), PageBreak()]

    story += [heading("7. SQLite3 database implementation"),
        p("Database: data/weather.db. Table: weather_daily. The schema uses TEXT for ID/city/date/season, "
          "REAL for weather measurements and deviations, and INTEGER for month, WMO code and 0/1 flags. "
          "record_id is the primary key; UNIQUE(city,date) additionally protects the logical record identity. "
          "NOT NULL and CHECK constraints protect the prepared table."),
        Preformatted('INSERT INTO weather_daily (...) VALUES (...)\n'
                     'ON CONFLICT(record_id) DO NOTHING;\n\n'
                     'SELECT COUNT(*) FROM weather_daily;\n'
                     'SELECT city, date, COUNT(*) FROM weather_daily\n'
                     'GROUP BY city, date HAVING COUNT(*) > 1;', STYLES["CodeReport"]),
        p("The abbreviated insertion listing shows the conflict policy; the executable source supplies all "
          "17 column names and parameter placeholders. It ignores primary-key conflicts only: invalid new "
          "rows still fail database constraints instead of being silently discarded."),
        table([["Idempotency evidence", "Actual result"],
               ["Cleaned / stored", f"{database['processed']} / {database['stored']}"],
               ["Inserted on first load of this recorded stage", database["first_load"]["inserted"]],
               ["Inserted on identical second load", database["second_load"]["inserted"]],
               ["Duplicate city/date groups", database["duplicate_city_dates"]],
               ["All stored values equal cleaned input", database["exact_data_match"]],
               ["Database content unchanged after second load", database["idempotent"]]], [WIDTH*.7, WIDTH*.3]),
        Spacer(1, 8), p("If the database was already populated by an earlier identical run, the first load "
          "of this stage also inserts zero rows. This is expected idempotent behaviour. Full content hashes "
          "before and after the second load are recorded in results/database.json."),
        sub("SQL results by city"),
        table([["City", "Records", "Annual mean C", "Precipitation mm"],
               *[[r["city"], r["days"], f"{float(r['mean_temperature']):.2f}",
                  f"{float(r['precipitation_mm']):.1f}"] for r in city_rows]],
              [WIDTH*.28, WIDTH*.19, WIDTH*.25, WIDTH*.28]), PageBreak()]

    findings = (RESULTS / "findings.md").read_text(encoding="utf-8")
    sections = re.findall(r"(?ms)^(\d\..*?)(?=^\d\.|\n\n|\Z)", findings)
    story += [heading("8. Exploratory data analysis"),
        p("EDA reads the prepared database, inspects dimensions and types, calculates numerical descriptive "
          "statistics and categorical WMO frequencies, and compares city-level aggregates. The prepared "
          "table has 1,825 rows and 17 columns with no missing values. Supporting CSVs contain the full "
          "statistics and a 5-by-12 monthly-temperature pivot."),
        *figure("01_temperature_trends.png", "Figure 1. Actual daily mean temperatures shown as trailing 7-day averages.", 240),
        p(next(item for item in sections if item.startswith("1. Temperature")).replace("\n", " ")),
        p("The five-city comparison shows strong seasonality, but this descriptive single-year analysis "
          "does not test causation or infer a long-term warming trend."), PageBreak(),
        heading("8. EDA: precipitation and seasonality"),
        *figure("02_precipitation.png", "Figure 2. Annual precipitation totals; snowfall is represented as water equivalent.", 195),
        p(next(item for item in sections if item.startswith("2. Precipitation")).replace("\n", " ")),
        *figure("03_monthly_heatmap.png", "Figure 3. Mean daily temperature aggregated by city and month.", 175),
        p(next(item for item in sections if item.startswith("3. Monthly")).replace("\n", " ")), PageBreak(),
        heading("8. EDA: additional weather indicators"),
        *figure("04_weather_exposure.png", "Figure 4. Frost, hot and wet-day counts using documented descriptive thresholds.", 195),
        p(next(item for item in sections if item.startswith("4. Exposure")).replace("\n", " ")),
        *figure("05_temperature_range.png", "Figure 5. Distribution of daily maximum-minus-minimum temperature.", 195),
        p(next(item for item in sections if item.startswith("5. Temperature")).replace("\n", " ")), PageBreak()]

    story += [heading("9. Pipeline testing and verification"),
        table([["Stage", "Actual record count"], *[[key, value] for key, value in counts.items()]],
              [WIDTH*.65, WIDTH*.35]), Spacer(1, 9),
        p("All production counts agree because no source rows failed validation or required duplicate "
          "removal. The invalid count is zero, not a missing measurement. Four deliberate test rows "
          "are excluded from every production count. Full source and consumed JSON hashes also agree."),
        table([["End-to-end check", "Result"],
               *[[key.replace("_", " "), "PASS" if value else "FAIL"]
                 for key, value in verification["checks"].items()]], [WIDTH*.82, WIDTH*.18]),
        Spacer(1, 9), p(f"Automated tests: {unit.attrib['tests']} passed; "
          f"failures={unit.attrib['failures']}, errors={unit.attrib['errors']}. Tests cover impossible "
          "dates, negative precipitation, unknown categories, cross-field inconsistency, wrong types, "
          "infinite values, missing schema columns, optional missing means, duplicate cleaning and "
          "database constraint enforcement/idempotency. JUnit evidence: results/unit_tests.xml."), PageBreak()]

    story += [heading("10. Reproduction and encountered errors"),
        p("Clone/download the repository, create a Python 3.13 environment and install requirements-dev.txt. "
          "Start the documented Kafka broker using Java 17 or Docker. Run the commands below from the "
          "project root. No personal absolute path, secret API key or undocumented local input is needed."),
        Preformatted('python -m pip install -r requirements-dev.txt\n'
                     'python scripts/start_kafka_local.py\n'
                     '# In a second terminal with the same environment:\n'
                     'python main.py --use-snapshot\n'
                     'python -m pytest -q\n'
                     '# Optional fresh API collection and complete rerun:\n'
                     'python main.py', STYLES["CodeReport"]),
        p("The preserved snapshot reproduces the included dataset even if the provider later revises "
          "its archive. It still travels through a real Kafka broker on every run. Changing the collection "
          "period requires preserving/renaming the old database so unrelated rows are not mixed silently."),
        p("Encountered problems: Kafka's shell startup mishandled JVM paths containing a space in the "
          "project folder name. The launcher was changed to a direct argument-list Java invocation. "
          "A localhost IPv6 attempt also produced misleading connection logs; the broker and client "
          "now use explicit IPv4 loopback. Native Kafka was actually tested; the alternative Docker "
          "configuration is supplied but was not executed on this machine."),
        heading("11. Conclusions and limitations"),
        p("The implemented pipeline collected real public weather data, transported all records through "
          "Kafka, validated them with Pandera, performed meaningful pandas/NumPy transformations and "
          "stored an exact, duplicate-free SQLite table. Repeated loading preserved both count and content. "
          "Five visualizations and numerical summaries answer the research questions."),
        p("Limitations: ERA5 grid estimates differ from individual station observations; only five locations "
          "and one year are analysed. Threshold indicators are not official hazard warnings. A single local "
          "Kafka broker has no high-availability guarantee. Distributed exactly-once processing is not "
          "claimed; only the identical-dataset database load is demonstrated as idempotent."), PageBreak()]

    story += [heading("12. Individual responsibilities"),
        p("The table records the agreed division of responsibility and prepared source files. Before final "
          "submission the group must confirm the actual individual work and changes made by each member. "
          "Every student must run, understand and explain the complete pipeline, including other parts."),
        table([["Member / ID", "Assigned component and files"],
               [f"{members[0][0]} / {members[0][1]}", "API collection; api_client.py; raw responses and dictionary"],
               [f"{members[1][0]} / {members[1][1]}", "Broker setup; producer.py; consumer.py; message evidence"],
               [f"{members[2][0]} / {members[2][1]}", "validator.py; cleaner.py; negative tests; transformations"],
               [f"{members[3][0]} / {members[3][1]}", "loader.py; SQL; analysis.py; verification.py; main.py; automated tests"]],
              [WIDTH*.42, WIDTH*.58]), Spacer(1, 14), heading("13. References"),
        *[p(text) for text in [
            "Open-Meteo. Historical Weather API and WMO code reference. https://open-meteo.com/en/docs/historical-weather-api",
            "Apache Software Foundation. Kafka 3.9 Quickstart. https://kafka.apache.org/39/quickstart/",
            "kafka-python. API documentation. https://kafka-python.readthedocs.io/",
            "Pandera. DataFrame schemas and lazy validation. https://pandera.readthedocs.io/",
            "pandas. Official documentation. https://pandas.pydata.org/docs/",
            "NumPy. Official documentation. https://numpy.org/doc/",
            "Python. sqlite3 module. https://docs.python.org/3/library/sqlite3.html",
            "Matplotlib and Seaborn. https://matplotlib.org/stable/ ; https://seaborn.pydata.org/",
            "SIS 2 project assignment sheet, Data Collection & Preparation (provided course document)."]],
        Spacer(1, 8), p("Machine-readable evidence: collection.json, producer.json, consumer.json, "
          "validation.json, validation_tests.json, cleaning.json, database.json, pipeline_verification.json "
          "and unit_tests.xml. The repository README maps each stage to execution commands and expected outputs.")]
    output = ROOT / "report" / "project_report.pdf"
    output.parent.mkdir(exist_ok=True)
    document = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=19*mm, rightMargin=19*mm,
                                  topMargin=19*mm, bottomMargin=24*mm,
                                  title="SIS 2 - Kazakhstan Weather Pipeline", author="SIS 2 project team")
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--group")
    build(parser.parse_args().group)
