
# 小規模ツールテンプレート

## 1. 概要
- **目的**：CSVファイルを監視し、BOXへアップロードする簡易ツール。
- **対象業務**：データ転送の自動化。
- **開発規模**：小規模（個人利用）。

## 2. 要件定義
### 機能要件
- [ ] 指定フォルダのCSV監視
- [ ] BOXへのアップロード
- [ ] ログ出力（任意）

### 非機能要件
- OS：Windows 10以上
- 言語：Python 3.9+

## 3. 設定項目（config.json）
- watch_folder：監視対象フォルダ
- box_upload_url：BOX共有リンク
- log_level：INFO/ERROR

## 4. 簡易設計
### フォルダ構成
```
small-tool-template/
├─ README.md
├─ config.json
├─ main.py
└─ modules/
   └─ uploader.py
```

### データフロー
1. main.pyで監視開始
2. 新しいCSV検出 → uploader.pyでBOXへ送信

## 5. 運用
- 実行方法：`python main.py`
- 自動起動：タスクスケジューラ（任意）
