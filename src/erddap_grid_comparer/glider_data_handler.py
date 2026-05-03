import pandas as pd
from erddap_grid_comparer.erddap_wrapper import ErddapIngestor, GLIDER_URL

def get_glider_datasets() -> pd.DataFrame:
    ingestor = ErddapIngestor(GLIDER_URL)
    return ingestor.dataset_search()[['Title','Summary','Institution']]

def get_glider_dataset_institutions() -> set[str]:
    institutions = list(get_glider_datasets()['Institution'].unique())
    institutions = {insta for row in institutions for insta in row.split(',')}
    return institutions


if __name__ == "__main__":
    get_glider_datasets().to_csv('glider_datasets.csv')