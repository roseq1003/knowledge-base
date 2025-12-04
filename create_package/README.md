# Pythonパッケージ構造自動生成ツール

このツールは、標準的なPythonパッケージ構造を自動的に作成します。開発の初期段階で、ディレクトリや設定ファイルを手動で準備する手間を省くことができます。

---

## 📌 主な機能
- 以下のディレクトリを自動生成
  - `src/<パッケージ名>/modules`（モジュール用）
  - `src/<パッケージ名>/utils`（ユーティリティ用）
  - `src/<パッケージ名>/config`（設定ファイル）
  - `tests/`（テストコード）
  - `assets/`, `build/`, `log/`（補助ディレクトリ）
  - `venv/`（仮想環境用プレースホルダ）
- 以下のファイルを自動生成
  - `pyproject.toml`（PEP 621準拠）
  - `README.md`
  - `.gitignore`
  - `.env`
  - 設定ファイル（`default.json`, `production.json`）
  - サンプルテストファイル
- シンプルな `main.py` エントリーポイントを追加
- 依存パッケージ、著者名、メールアドレスを指定可能

---

## 📂 生成されるディレクトリ構造
```
my_package/
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── main.py
│       ├── modules/
│       ├── utils/
│       └── config/
│           ├── default.json
│           └── production.json
├── tests/
│   └── test_sample.py
├── assets/
├── build/
├── log/
├── venv/
├── pyproject.toml
├── README.md
├── .gitignore
└── .env
```

---

## 🚀 使い方
```bash
python create_package.py --name my_package \
    --deps requests,pandas \
    --author-name "川野 宏太" \
    --author-email "~~~~@~~~.co.jp"
```
