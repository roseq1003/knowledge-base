
# プロジェクト名（例：Particle Monitoring Helper）

## 1. 概要
- **目的**：測定器のCSVを監視し、閾値超過や更新停止を検知してTeamsに通知し、BOXへ自動アップロードする。
- **対象業務**：製造現場のパーティクル監視の運用支援。
- **開発規模**：小〜中規模（個人ツール）。
- **前提**：
  - 測定器はメーカー提供実行ファイルでCSV追記（1分周期）。
  - ローカルPCで常駐Pythonスクリプトを運用。
  - クラウドAPIは最小限（BOX、Teams Webhook）。

---

## 2. 要件定義（最小）
### 2.1 機能要件
- [ ] CSVの更新監視（最終更新時刻のチェック）
- [ ] CSV内容の解析（閾値超過の連続判定）
- [ ] Teamsへの通知（Webhook）
- [ ] BOXへの自動アップロード（ファイル更新・切替に追随）
- [ ] ログ出力（INFO/ERROR）

### 2.2 非機能要件
- OS：Windows 10 以上
- 実行：常駐（タスクスケジューラ or スタートアップ）
- パフォーマンス：1分周期で検査／通知遅延1分以内
- セキュリティ：トークン／Webhook URLは環境変数 or 設定ファイルで秘匿

### 2.3 制約条件
- 測定器側のCSV仕様は変更不可
- 社内ネットワーク（ドメイン参加）で運用
- 長期運用前提（ログローテーションを推奨）

---

## 3. 方式設計（最小）
### 3.1 フォルダ構成
```
project-root/
├─ main.py                 # メインループ（監視・解析・通知）
├─ config.json             # 閾値・列名・IPなど設定
├─ modules/
│  ├─ upload_checker.py    # CSV更新監視
│  ├─ data_monitor.py      # 内容解析（閾値判定）
│  ├─ box_client.py        # BOXアップロード
│  ├─ teams_notifier.py    # Teams通知(Webhook)
│  └─ utils.py             # 共通処理（ログ、時刻、ファイル操作）
├─ logs/                   # ログ保管（ローテーション推奨）
├─ raw_data/               # 測定器のCSV配置フォルダ（監視対象）
└─ assets/                 # ハード資産管理（テンプレート/台帳）
```

### 3.2 データフロー（要点）
1. `upload_checker.py` が対象CSVの最終更新時刻を監視  
2. 未更新が閾値（例：10分）超え → Teams通知  
3. 更新中なら `data_monitor.py` が内容チェック（連続Nレコード閾値超過）  
4. 閾値超過連続検出 → Teams通知  
5. ファイル切り替え・一定容量到達 → `box_client.py` でBOXへアップロード

### 3.3 設定ファイル（例：`config.json`）
```json
{
  "watch_folder": "C:/Users/k_kawano1/Desktop/Particle monitoring system/raw data",
  "timestamp_column": "timestamp",
  "column_concentration_05": "濃度(LED)",
  "monitor_1": "192.168.0.101",
  "monitor_2": "192.168.0.102",
  "concentration_threshold_ng": 100,
  "consecutive_threshold_count": 10,
  "upload_idle_minutes": 10,
  "teams_webhook_url": "https://.../webhookb2/...",
  "box_upload_target_url": "https://hiratacojp.box.com/s/...",
  "log_level": "INFO"
}
```

---

## 4. 基本設計（必要な場合のみ、簡易表で管理）
### 4.1 入出力仕様（例）
| 対象 | 入力 | 出力 | 備考 |
|---|---|---|---|
| upload_checker | CSVファイルパス | 更新有無（bool） | 未更新閾値を超えたら通知 |
| data_monitor | CSV内容（行/列） | 連続超過判定（bool） | 連続Nレコード |
| teams_notifier | メッセージ文字列 | 送信結果（bool） | Webhook POST |
| box_client | ファイルパス | アップロード結果（bool） | ファイル切替時 |

### 4.2 画面/UI
- なし（常駐ツール）。ログとTeams通知のみ。

---

## 5. 詳細設計の扱い（簡易）
- 関数仕様は **コードのdocstring** に記載（引数、戻り値、例外、使用例）。
- 処理フローは **モジュール冒頭のコメント** に要約。
- 設計書の重複は避ける（READMEは変更頻度低い内容のみに絞る）。

---

## 6. 運用
- 起動方法：`python main.py`
- 自動起動：タスクスケジューラに登録（1分毎／常時実行）
- ログ運用：週次でローテーション、異常時のみTeams通知

---

## 7. ハードあり案件用セクション（充実版）
ハード資産情報は `assets/` 配下に **台帳（CSV/Markdown）** として管理します。Git管理可能な形で、設置変更やIP変更にも追従できます。

### 7.1 登録項目（推奨）
- 資産番号（Asset ID）
- 機器種別（測定器/産業用PC/スイッチ等）
- 設置場所（拠点/建屋/ライン/座標 or 棚番号）
- 固定IP / サブネット / ゲートウェイ
- MACアドレス（可能なら）
- 連絡先（管理者/担当者）
- 導入日 / 更新日
- 備考（UPS有無、耐環境条件など）

### 7.2 記入ルール
- IPはCIDR表記でサブネットも併記（例: `192.168.0.101/24`）。
- 設置場所は「拠点>建屋>ライン>機器位置」の階層で記載。
- 変更があった場合は **PR/コミットメッセージに理由を明記**。

### 7.3 台帳ファイル
- `assets/hardware_assets.csv`：一覧管理用（Excel互換）
- `assets/asset_XXXX.md`：機器単位の詳細（テンプレートから生成）

### 7.4 例：CSVテンプレート（抜粋）
```csv
asset_id,category,model_name,serial_no,location_site,location_building,location_line,location_spot,fixed_ip,cidr,gateway,mac_address,admin_name,admin_email,installed_date,updated_date,notes
A-0001,particle_monitor,Model-X,PM123456,本社,第一工場,ラインA,検査位置1,192.168.0.101,24,192.168.0.1,00:11:22:33:44:55,川野 宏太,k_kawano1@hirata.co.jp,2025-10-01,2025-12-04,UPSあり; 耐環境0-40℃
A-0002,industrial_pc,IPC-700,IPC98765,本社,第一工場,ラインA,制御盤内,192.168.0.50,24,192.168.0.1,AA:BB:CC:DD:EE:FF,川野 宏太,k_kawano1@hirata.co.jp,2025-10-01,2025-12-04,ドメイン参加; 有線LAN
```

### 7.5 機器詳細テンプレート（`assets/asset_TEMPLATE.md`）
```markdown
# 資産詳細（Asset ID: {{asset_id}}）

## 1. 基本情報
- 機器種別：
- メーカー/型式：
- シリアル：
- 資産番号（社内台帳）：

## 2. 設置情報
- 拠点：
- 建屋：
- ライン：
- 位置（棚/座標/盤内）：
- 設置写真：`assets/photos/{{asset_id}}.jpg`（任意）

## 3. ネットワーク
- 固定IP：
- サブネット（CIDR）：
- ゲートウェイ：
- MACアドレス：
- ドメイン参加：はい/いいえ

## 4. 管理
- 管理者：
- 連絡先メール：
- 導入日：
- 最終更新日：

## 5. 備考
- UPS有無：
- 耐環境：
- その他：
```

---

### 7.6 運用のポイント
- 機器交換やIP変更時は **CSVと該当Markdownを同時更新**。
- Teams通知の宛先リストは資産CSVの `admin_email` を参照する運用も可。
- 写真や図面は `assets/photos/` に保存（Git LFSの利用を推奨）。
