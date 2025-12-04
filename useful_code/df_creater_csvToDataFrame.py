# csvをオープンして、加工したら戻り値としてdfを返すよ。
# 割と単体で使えるモジュール(I/Oを分けていないモジュール

# ちょっとmonitoringシステムと異なるdfの作成をしている点に注意～
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

from sub import config_loader
from typing import Dict, List, Tuple

# 自作モジュール
from . import logger as log, config_loader

# 設定読み込み
config = config_loader.load_config()
logger = log.get_logger("df_creator")

# --- CSV読み込みと構造抽出 ---
def _read_csv_rows(csv_path: str, ip_row_index, header_row_index) -> Tuple[pd.DataFrame, List[str], List[str]]:
    logger.info(f"CSV読み込み開始: {csv_path}")
    df = pd.read_csv(csv_path, encoding='utf-8', header=None)
    if df.empty:
        logger.error("CSVが空です")
        raise ValueError("CSVが空です")

    n_rows = len(df)
    if ip_row_index >= n_rows or header_row_index >= n_rows:
        logger.error("指定行がCSVの行数を超過")
        raise ValueError("IP行/ヘッダー行の位置が不正です")

    if header_row_index <= ip_row_index:
        logger.error("ヘッダー行はIP行より後の行である必要があります")
        raise ValueError("ヘッダー行はIP行より後の行である必要があります")

    ip_row_list = df.iloc[ip_row_index].tolist() # csvの1行目(ip行)をリスト化
    header_row_list = df.iloc[header_row_index].tolist() # ヘッダー行をリスト化
    data_start_index = header_row_index + 1 # データ開始行indexを決定、ヘッダーの次行から
    data_df = df.iloc[data_start_index:].reset_index(drop=True) # スタートインデックスから抜き取ってindex初期化

    logger.debug(f"IP行index: {ip_row_index} / ヘッダー行index: {header_row_index}")
    return data_df, ip_row_list, header_row_list

# --- ヘッダー行からインデックスマップ作成 ---
def _build_col_index_map(header_row_list: List[str]) -> Dict[str, int]:
    return {name: idx for idx, name in enumerate(header_row_list) if name not in header_row_list[:idx]}

# --- タイムスタンプ生成 ---
def _create_timestamp_df(data_df: pd.DataFrame, date_col_index: int, time_col_index: int, num_col_index: int) -> Tuple[pd.DataFrame, int]:
    column_num_name = config['column_number']
    column_date_name = config['column_date']
    column_time_name = config['column_time']

    selected_df = data_df.iloc[:, [num_col_index, date_col_index, time_col_index]].copy()
    selected_df.columns = [column_num_name, column_date_name, column_time_name]

    selected_df["timestamp"] = pd.to_datetime(
        selected_df[column_date_name].astype(str) + " " + selected_df[column_time_name].astype(str),
        errors="coerce"
    )
    nat_cnt = int(selected_df["timestamp"].isna().sum())
    selected_df = selected_df.dropna(subset=[column_num_name])

    return selected_df[[column_num_name , "timestamp"]], nat_cnt

# --- モニターごとの列幅推定 ---
def _estimate_num_cols_per_monitor(ip_row_list: List[str], ip_list_byDict: List[str]) -> int:
    ip_positions = [i for i, val in enumerate(ip_row_list) if val in ip_list_byDict]
    if len(ip_positions) < 2: # モニターが１個しかないなら、
        return config['dataframe_num_columns']
    return ip_positions[1] - ip_positions[0] - 1

# --- IPごとのデータ抽出 ---
def _extract_ip_column_ranges(
    data_df: pd.DataFrame,
    ip_row_list: List[str],
    header_row_list: List[str],
    ip_list_byDict: list[str],
    num_col_index: int,
    num_cols_per_monitor: int,
) -> Tuple[Dict[str, pd.DataFrame], List[str]]:
    result_dfs: Dict[str, pd.DataFrame] = {}
    missing_ips: List[str] = []

    for ip in ip_row_list:
        if ip not in ip_list_byDict:
            continue
        try:
            start_idx = ip_row_list.index(ip)
        except ValueError:
            missing_ips.append(ip)
            continue

        end_idx = min(start_idx + num_cols_per_monitor, len(header_row_list))
        use_cols = [num_col_index] + list(range(start_idx, end_idx))
        sub_df = data_df.iloc[:, use_cols].copy()
        sub_df.columns = [header_row_list[num_col_index]] + header_row_list[start_idx:end_idx]

        if header_row_list[num_col_index] != config['column_number']:
            sub_df.rename(columns={header_row_list[num_col_index]: config['column_number']}, inplace=True)

        sub_df = sub_df.dropna(subset=[config['column_number']])
        result_dfs[ip] = sub_df

    return result_dfs, missing_ips

# --- メイン処理（1ファイル） ---
def _build_merged_tables(latest_csv: str) -> Tuple[Dict[str, pd.DataFrame], Dict[str, object]]:
    ip_row_index = config['csv_ip_row'] # ip行のこと index 0
    header_row_index = config['csv_header_row'] # ヘッダー行のこと index 1
    column_date = config['column_date'] # カラム名："日時"
    column_time = config['column_time'] # カラム名："時間"
    column_number = config['column_number'] # カラム名："番号"
    ip_list_byDict = [monitor["ip"] for monitor in config["dict_monitors"].values()] # 辞書にあるipリスト

    data_df, ip_row_list, header_row_list = _read_csv_rows(csv_path=latest_csv, ip_row_index=ip_row_index, header_row_index=header_row_index) # 1csvを1つのdfにする。
    col_name_to_index = _build_col_index_map(header_row_list) # ヘッダーのカラムを辞書化、キー：カラム名、バリュー：インデックス

    # 日時・時間・番号列のインデックスを取得する。
    try:
        date_col_index = col_name_to_index[column_date]
        time_col_index = col_name_to_index[column_time]
        num_col_index  = col_name_to_index[column_number]
    except KeyError as e:
        raise KeyError(f"必須列名がヘッダー行に見つかりません: {e}")

    # タイムスタンプのdfを取得
    timestamp_df, nat_cnt = _create_timestamp_df(data_df, date_col_index, time_col_index, num_col_index)
    num_cols_per_monitor = _estimate_num_cols_per_monitor(ip_row_list, ip_list_byDict)

    # データ部の抜き出し
    extracted_dfs, missing_ips = _extract_ip_column_ranges(
        data_df, ip_row_list, header_row_list, ip_list_byDict, num_col_index, num_cols_per_monitor
    )

    # タイムスタンプとデータ部を結合
    merged_dfs: Dict[str, pd.DataFrame] = {}
    rows_after_dropna_number: Dict[str, int] = {}
    for ip, sub_df in extracted_dfs.items():
        merged_df = pd.merge(timestamp_df, sub_df, on=config['column_number'], how="inner") # 分離したdf(timestampとデータ部)を結合する。
        merged_dfs[ip] = merged_df
        rows_after_dropna_number[ip] = len(sub_df)

    diagnostics = {
        "missing_ips": missing_ips,
        "timestamp_nat_count": nat_cnt,
        "rows_after_dropna_number": rows_after_dropna_number,
        "ip_row_index": ip_row_index,
        "header_row_index": header_row_index,
        "estimated_num_cols_per_monitor": num_cols_per_monitor,
        "col_name_index": col_name_to_index
    }

    print(diagnostics)

    return merged_dfs, diagnostics

# --- 複数CSV対応処理 ---
def build_all_merged_tables() -> Dict[str, pd.DataFrame]:
    
    # 下準備、こいつが戻り値になる(全ての単一のdfをマージして、各ipをキー、値をdfとした辞書型のオブジェクトを返す。)。
    all_merged: Dict[str, pd.DataFrame] = {}

    # csvファイルを選択するダイアログを開く
    file_paths = filedialog.askopenfilenames(title="CSVファイルを選択", filetypes=[("CSV Files", "*.csv")]) # ダイアログを開いてユーザーからファイルパスを取得させる
    print(f'file_pathsはこれ{file_paths}')

    # file_pathsがあれば、処理開始～～
    if file_paths:
        for path in file_paths:
            try:
                merged_dfs, _ = _build_merged_tables(path) # diafnosticsは無視してok
                for ip, df in merged_dfs.items(): # マージしたdfsからipとdfを抜き取り。。。
                    if ip not in all_merged: # そのipがall_mergedにない場合
                        all_merged[ip] = df # 新しくall_mergedにキーを設定してdfをいれこむ(新しいキーに新しいdfを入れ込む感じ)
                    else:
                        all_merged[ip] = pd.concat([all_merged[ip], df], ignore_index=True) # ipが存在する場合（すでに読み込んでるなら)、concatする。
                        all_merged[ip].drop_duplicates(subset=["timestamp"], keep="last") # timestampは絶対に重複しないので重複は削除

            except Exception as e: # raiseされたらここに記述してくよ。
                logger.error(f"ファイル {path} の処理中にエラFー: {e}")
                messagebox.showwarning(f"ファイル {path} の処理中にエラー: {e}")

    else:
        messagebox.showwarning("警告", "データが存在しません。")

    # 重複は消すよ～ん

    # 各IPごとにtimestampでソート。時系列データなので、昇順にする
    for ip in all_merged:
        all_merged[ip] = all_merged[ip].sort_values("timestamp").reset_index(drop=True) # 元のインデックスは捨てる(デフォルト)。

    return all_merged


# # 単体テスト君, 本番環境ではコメントアウトしてね
# all_merged=build_all_merged_tables()
# print(all_merged)