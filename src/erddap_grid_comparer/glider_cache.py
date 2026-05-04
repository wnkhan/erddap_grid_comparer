from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Iterable

import pandas as pd

from erddap_grid_comparer.erddap_wrapper import ErddapIngestor


def build_grid_dataset_map(glider_datasets: pd.DataFrame) -> dict[str, list[str]]:
    return glider_datasets.groupby("grid_label")["Dataset ID"].agg(list).to_dict()


def grid_cache_dir(cache_root: str | Path, grid_label: str) -> Path:
    return Path(cache_root) / grid_label


def dataset_cache_path(cache_root: str | Path, grid_label: str, dataset_id: str) -> Path:
    return grid_cache_dir(cache_root, grid_label) / f"{dataset_id}.csv"


def fetch_dataset_rows(
    ingestor: ErddapIngestor,
    dataset_id: str,
    variables: Iterable[str],
) -> pd.DataFrame:
    glider_data = ingestor.get_dataset(dataset_id, list(variables))
    return glider_data.iloc[1:, :].copy()


def write_grid_cache(
    cache_root: str | Path,
    grid_label: str,
    dataset_ids: Iterable[str],
    ingestor: ErddapIngestor,
    variables: Iterable[str],
    *,
    refresh: bool = False,
    max_workers: int = 8,
) -> list[str]:
    dataset_ids = list(dataset_ids)
    grid_dir = grid_cache_dir(cache_root, grid_label)
    grid_dir.mkdir(parents=True, exist_ok=True)

    pending_dataset_ids = [
        dataset_id
        for dataset_id in dataset_ids
        if refresh or not dataset_cache_path(cache_root, grid_label, dataset_id).exists()
    ]

    if pending_dataset_ids:
        worker_count = min(max_workers, len(pending_dataset_ids)) or 1
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            for dataset_id, glider_data_df in zip(
                pending_dataset_ids,
                executor.map(
                    lambda current_dataset_id: fetch_dataset_rows(
                        ingestor,
                        current_dataset_id,
                        variables,
                    ),
                    pending_dataset_ids,
                ),
            ):
                glider_data_df.to_csv(
                    dataset_cache_path(cache_root, grid_label, dataset_id),
                    index=False,
                )

    (grid_dir / "_datasets.txt").write_text("\n".join(dataset_ids) + "\n")
    return sorted(path.name for path in grid_dir.glob("*.csv"))


def build_cache(
    cache_root: str | Path,
    grid_to_datasets: dict[str, list[str]],
    ingestor: ErddapIngestor,
    variables: Iterable[str],
    *,
    refresh: bool = False,
    max_workers: int = 8,
) -> int:
    cache_root = Path(cache_root)
    cache_root.mkdir(parents=True, exist_ok=True)

    for grid_label, dataset_ids in grid_to_datasets.items():
        write_grid_cache(
            cache_root=cache_root,
            grid_label=grid_label,
            dataset_ids=dataset_ids,
            ingestor=ingestor,
            variables=variables,
            refresh=refresh,
            max_workers=max_workers,
        )

    return sum(1 for _ in cache_root.glob("*/*.csv"))


def load_grid_data(cache_root: str | Path, grid_label: str, **read_csv_kwargs) -> pd.DataFrame:
    grid_dir = grid_cache_dir(cache_root, grid_label)
    dataset_paths = sorted(grid_dir.glob("*.csv"))
    if not dataset_paths:
        raise FileNotFoundError(
            f"No cached datasets found for {grid_label}. Run the cache build step first."
        )

    return pd.concat(
        (pd.read_csv(dataset_path, **read_csv_kwargs) for dataset_path in dataset_paths),
        ignore_index=True,
    )


def load_dataset_data(
    cache_root: str | Path,
    grid_label: str,
    dataset_id: str,
    **read_csv_kwargs,
) -> pd.DataFrame:
    dataset_path = dataset_cache_path(cache_root, grid_label, dataset_id)
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"No cached dataset found for {dataset_id} in {grid_label}. "
            "Run the cache build step first."
        )

    return pd.read_csv(dataset_path, **read_csv_kwargs)


def list_grid_dataset_ids(cache_root: str | Path, grid_label: str) -> list[str]:
    grid_dir = grid_cache_dir(cache_root, grid_label)
    manifest_path = grid_dir / "_datasets.txt"

    if manifest_path.exists():
        dataset_ids = [line.strip() for line in manifest_path.read_text().splitlines() if line.strip()]
        if dataset_ids:
            return dataset_ids

    return sorted(path.stem for path in grid_dir.glob("*.csv"))


def list_grid_labels(cache_root: str | Path) -> list[str]:
    cache_root = Path(cache_root)
    if not cache_root.exists():
        return []

    return sorted(path.name for path in cache_root.iterdir() if path.is_dir())


def dataset_ids_by_grid(cache_root: str | Path) -> dict[str, list[str]]:
    return {
        grid_label: list_grid_dataset_ids(cache_root, grid_label)
        for grid_label in list_grid_labels(cache_root)
    }


def load_grid_datasets(
    cache_root: str | Path,
    grid_label: str,
    **read_csv_kwargs,
) -> dict[str, pd.DataFrame]:
    dataset_ids = list_grid_dataset_ids(cache_root, grid_label)
    if not dataset_ids:
        raise FileNotFoundError(
            f"No cached datasets found for {grid_label}. Run the cache build step first."
        )

    return {
        dataset_id: load_dataset_data(
            cache_root=cache_root,
            grid_label=grid_label,
            dataset_id=dataset_id,
            **read_csv_kwargs,
        )
        for dataset_id in dataset_ids
    }
