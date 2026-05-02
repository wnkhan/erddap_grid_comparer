from erddap_grid_comparer.erddap_wrapper import ErddapIngestor, GLIDER_URL

def get_glider_datasets():
    ingestor = ErddapIngestor(GLIDER_URL)
    return ingestor.dataset_search(
        max_lon=-50,
        min_lon=-120,
        max_lat=60,
        min_lat=0
    )

def get_erddap_data_servers():
    return ErddapIngestor(GLIDER_URL).get_servers()


if __name__ == "__main__":
    print(get_erddap_data_servers())