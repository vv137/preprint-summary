import datetime
import logging
import zoneinfo

import feedparser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def fetch_arxiv_preprints(
    category: str,
    submitted_date_str: str,
    # max_results: int = 100,
) -> list[dict[str, str]]:
    """
    Fetches arXiv preprints from the given category that were published on the specified date.

    Parameters:
        category (str): The arXiv category (e.g., 'cs.AI', 'physics.gen-ph').
        date_str (str): The publication date to filter by, in 'YYYY-MM-DD' format.
        max_results (int): Maximum number of results to retrieve.
    """
    # Convert date_str to a datetime.date object.
    target_date = datetime.datetime.strptime(submitted_date_str, r"%Y-%m-%d").date()

    # Build the API query URL. The search_query parameter 'cat:category' restricts to the given category.
    # base_url = "http://export.arxiv.org/api/query?"
    # query = f"search_query=cat:{category}&start=0&max_results={max_results}&sortBy=lastUpdatedDate&sortOrder=descending"
    # url = base_url + query
    base_url = "https://rss.arxiv.org/atom/"
    url = base_url + category

    logging.info(url)

    # Parse the feed.
    feed = feedparser.parse(url)

    papers = []

    # Iterate over the entries and filter by publication date.
    for entry in feed.entries:
        submission_datetime = datetime.datetime.strptime(
            entry.updated.__str__().split("T")[0], r"%Y-%m-%d"
        )
        submission_date = submission_datetime.date()
        if submission_date == target_date:
            title = entry.title.__str__().strip()
            authors = ", ".join(author.name.__str__() for author in entry.authors)
            abstract = entry.summary.__str__()
            url = entry.link
            papers.append(
                {
                    "title": title,
                    "category": category,
                    "authors": authors,
                    "datetime": target_date,
                    "abstract": abstract,
                    "url": url,
                }
            )

    return papers


def fetch_biorxiv_preprints(
    category: str,
    submitted_date_str: str,
) -> list[dict[str, str]]:
    target_date = datetime.datetime.strptime(submitted_date_str, "%Y-%m-%d").date()

    base_url = "http://connect.biorxiv.org/biorxiv_xml.php?subject="
    url = base_url + category

    logging.info(url)

    feed = feedparser.parse(url)

    papers = []

    # Iterate over the entries and filter by publication date.
    for entry in feed.entries:
        submission_datetime = datetime.datetime.strptime(
            entry.updated.__str__(), r"%Y-%m-%d"
        )
        submission_date = submission_datetime.date()
        if submission_date == target_date:
            title = entry.title.__str__().strip()
            authors = ", ".join(author.name.__str__() for author in entry.authors)
            abstract = entry.summary.__str__().strip()
            url = entry.link
            papers.append(
                {
                    "title": title,
                    "category": category,
                    "authors": authors,
                    "datetime": target_date,
                    "abstract": abstract,
                    "url": url,
                }
            )

    return papers


def generate_html(
    preprints: list[dict[str, str]],
    subtitle: str = "",
    contents_key: str = "abstract",
):
    # Start the HTML document with basic head elements and embedded CSS styling.
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preprints</title>
    <style>
        body {
            font-family: "Times New Roman", Times, serif;
            margin: 40px;
            background-color: #fdfdfd;
            color: #000;
            line-height: 1.6;
        }
        h1 {
            text-align: center;
            margin-bottom: 50px;
        }
        .preprint {
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 1px solid #ccc;
        }
        .preprint-title {
            font-size: 1.4em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .preprint-date {
            margin-bottom: 10px;
        }
        .preprint-authors {
            font-style: italic;
            margin-bottom: 10px;
        }
        .preprint-abstract {
            margin-top: 10px;
            font-size: 1em;
        }
    </style>
</head>
<body>
    """
    html_content += f"<h1>Preprints: {subtitle}</h1>"

    # Add each preprint to the HTML page.
    for preprint in preprints:
        html_content += f"""
    <div class="preprint">
        <div class="preprint-title"><a href="{preprint['url']}">{preprint['title']}</a></div>
        <div class="preprint-dates">{preprint['datetime']}</div>
        <div class="preprint-authors">{preprint['authors']}</div>
        <div class="preprint-abstract">{preprint[contents_key]}</div>
    </div>
        """

    # Close the HTML document.
    html_content += """
</body>
</html>
    """

    return html_content


def main():
    publication_date = (
        datetime.datetime.now(zoneinfo.ZoneInfo("America/New_York")).date()
    ).strftime(
        r"%Y-%m-%d"
    )  # Change this to the desired date (YYYY-MM-DD)
    # publication_date = "2025-04-01"
    logging.info(publication_date)
    papers = []

    # Fetch arXiv.
    # Specify the category and date you want to search for.
    categories = ["physics.bio-ph", "physics.chem-ph"] + ["cs.AI", "cs.LG"]
    if categories:
        new_papers = fetch_arxiv_preprints("+".join(categories), publication_date)
        papers.extend(new_papers)

    # Fetch bioRxiv.
    # Specify the category and date you want to search for.
    subjects = ["bioinformatics", "biophysics"]
    if subjects:
        new_papers = fetch_biorxiv_preprints("+".join(subjects), publication_date)
        papers.extend(new_papers)

    # Sort by date and time.
    papers.sort(key=lambda x: x["datetime"])

    # Remove duplicants.
    titles = set((i, e["title"]) for i, e in enumerate(papers))
    papers = [papers[i] for i, _ in titles]
    logging.info(f"Got {len(papers)} preprints")

    # Generate HTML content.
    html_content = generate_html(
        papers,
        contents_key="abstract",
        subtitle=", ".join(categories + subjects),
    )

    # Write the HTML content to a file.
    output_filepath = "report.html"
    with open(output_filepath, "w", encoding="utf-8") as file:
        file.write(html_content)
        logging.info(f"Report written in '{output_filepath}'")


# Example usage:
if __name__ == "__main__":
    main()
