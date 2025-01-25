from typing import List
import pandas as pd
import os
import datetime
import json
import pm4py
import shutil
import easygui

default_folder_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "datasets")
selected_folder = ""
meta_fields = []


class DataModel:

    def set_meta_fields(params: dict) -> None:
        global meta_fields
        meta_fields = params

    def normalize_data(
        a_log: pd.DataFrame,
        a_key: str,
        meta_fields: List[str] = ["txHash", "blockNumber",
                                  "contractAddress", "sender", "gasUsed", "activity", "timestamp"]
    ) -> pd.DataFrame:
        prefix = a_key.rstrip(
            's') + '_' if a_key.endswith('s') else a_key + '_'

        try:
            normalized_df = pd.json_normalize(
                a_log.to_dict('records'),
                record_path=a_key,
                meta=meta_fields,
                record_prefix=prefix,
                errors='ignore'
            )
            if not normalized_df.empty and 'txHash' in normalized_df:
                id_suffix = normalized_df.groupby("txHash").cumcount() + 1
                normalized_df[f"{prefix.rstrip('_')}__id"] = (
                    f"{prefix.rstrip('_')}_" +
                    normalized_df["txHash"] + "_" +
                    id_suffix.astype(str)
                )

            return normalized_df

        except KeyError as e:
            print(f"Warning: Key {a_key} not found in log structure")
            return pd.DataFrame()

        # self.path = easygui.fileopenbox(msg="Choose file", title="InsectaCam",  filetypes=[
            # "*.png", "*.jpg"], multiple=False, default="//*.png")
