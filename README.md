# insured-growth-app

日本株の上場企業について、被保険者数の過去分バックフィルを可視化するための、最小構成の `Python + Streamlit` アプリです。

このリポジトリは、まだ **バックフィル版** です。
将来の「日本年金機構の本線 collector」は **未実装** で、あとから追加しやすいように構成だけ分けています。

## このアプリでできること

- 2025-01 以降を対象に、月次の被保険者数データを可視化
- ダッシュボードで最新月の観測状況を確認
- 企業ランキングで増加企業を抽出
- セグメント別に観測率や純増を確認
- 企業詳細で推移、前月差、3か月純増、加速度、品質フラグを確認
- 監査キューで要確認データを洗い出し

## 現時点の前提

- 対象期間は **2025-01 から利用可能な最新月まで**
- 上場企業マスターは MVP では `data/listed_master_sample.csv` の手動配置を前提
- 過去分バックフィルのソースは `hokendb`
- 会社名一致だけで確定せず、`match_status` を保持
- 低母数ノイズや不確実なデータに備えて `quality_flag` を保持
- 将来は日本年金機構の本線 collector を追加予定

## ファイル構成

```text
insured-growth-app/
|-- app.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|-- data/
|   |-- listed_master_sample.csv
|   |-- company_match_sample.csv
|   |-- theme_map_sample.csv
|   `-- monthly_insured_sample.csv
|-- scripts/
|   |-- backfill_hokendb.py
|   `-- build_metrics.py
|-- src/
|   |-- loaders.py
|   |-- matching.py
|   |-- metrics.py
|   `-- quality.py
`-- tests/
    `-- test_metrics.py
```

## まず最初にやること

PowerShell を開いて、このリポジトリの場所へ移動します。

```powershell
cd D:\株アプリ\insured-growth-app
```

## Windows でのローカル実行手順

### 1. 仮想環境を作る

```powershell
py -m venv .venv
```

### 2. 仮想環境を有効化する

```powershell
.\.venv\Scripts\Activate.ps1
```

もし PowerShell の実行ポリシーで止まったら、次を実行してからもう一度有効化してください。

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 3. 依存ライブラリを入れる

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. サンプルデータから集計CSVを作る

```powershell
python scripts\build_metrics.py --input data\monthly_insured_sample.csv --output data\monthly_insured.csv
```

### 5. Streamlit を起動する

```powershell
streamlit run app.py
```

ブラウザで自動表示されない場合は、PowerShell に出る URL を開いてください。

通常は次のような URL です。

```text
http://localhost:8501
```

## データの流れ

### 1. 上場企業マスター

最小版では `data/listed_master_sample.csv` を使います。
将来は J-Quants ベースの更新に差し替えやすいようにしています。

主な列:

- `code`
- `company_name`
- `market`
- `sector17`
- `sector33`

### 2. マッチ補正

`data/company_match_sample.csv` で手動補正できます。

主な列:

- `source_company_name`
- `code`
- `match_status`
- `notes`

`match_status` 例:

- `matched`
- `manual_review`
- `uncertain`

### 3. 独自テーマ

`data/theme_map_sample.csv` でテーマを追加できます。

主な列:

- `code`
- `theme`

### 4. 月次データ

最終的に `data/monthly_insured.csv` を生成します。

出力列:

- `code`
- `company_name`
- `month`
- `insured_count`
- `mom_delta`
- `mom_ratio`
- `delta_3m`
- `accel_1m`
- `up_streak`
- `market`
- `sector17`
- `sector33`
- `theme`
- `source`
- `quality_flag`
- `match_status`
- `notes`

## スクリプト説明

### `scripts\backfill_hokendb.py`

`hokendb` の月次アーカイブや企業ページから取得するための **雛形スクリプト** です。

この最小版では、ネットワーク取得を必須にせず、次のような使い方を想定しています。

- ローカルの CSV を読み込む
- 将来、`hokendb` 取得処理をこのスクリプトへ追加する
- 取得後に標準化 CSV を保存する

サンプル実行:

```powershell
python scripts\backfill_hokendb.py --output data\monthly_insured_sample.csv
```

### `scripts\build_metrics.py`

元データからメトリクス列を作り、アプリ用の `monthly_insured.csv` を出力します。

```powershell
python scripts\build_metrics.py --input data\monthly_insured_sample.csv --output data\monthly_insured.csv
```

## 画面説明

### ダッシュボード

- 最新月
- 観測企業数
- セグメント別観測率
- 要確認件数

### 企業ランキング

- 前月比増加人数ランキング
- 前月比増加率ランキング
- 3か月純増ランキング
- 加速度ランキング
- 連続増加月数ランキング

### セグメント

- 市場区分
- 17業種
- 33業種
- 独自テーマ

表示項目:

- 観測企業数
- 母数
- 観測率
- 合計純増
- 中央増加率

### 企業詳細

- 月次被保険者数推移
- 前月差
- 3か月純増
- 加速度
- `quality_flag`
- `source`
- `notes`

### 監査キュー

- マッチ不確実
- 低信頼
- 変化が極端
- データ欠損あり

## エラー時の対処法

### `streamlit : 用語が認識されません`

仮想環境が有効になっていない可能性があります。

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

### `monthly_insured.csv が見つかりません`

先にメトリクス生成をしてください。

```powershell
python scripts\build_metrics.py --input data\monthly_insured_sample.csv --output data\monthly_insured.csv
```

### PowerShell でスクリプト実行が拒否される

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 文字化けが気になる

PowerShell 7 以上を使うか、UTF-8 で開けるエディタを使ってください。
CSV は UTF-8 を想定しています。

## テスト実行

最低限のメトリクス計算テストを 1 本入れています。

```powershell
pytest
```

## GitHub への push 手順

まだ GitHub リポジトリを作っていない場合は、先に GitHub 側で空のリポジトリを作成してください。

PowerShell で次を実行します。

```powershell
git init
git add .
git commit -m "Initial Streamlit MVP"
git branch -M main
git remote add origin https://github.com/<あなたのユーザー名>/<リポジトリ名>.git
git push -u origin main
```

もしこのローカルフォルダですでに `git init` 済みなら、`git init` は不要です。

## Streamlit Community Cloud デプロイ手順

### 1. GitHub に push する

この README の前の章の手順で、GitHub にコードを push します。

### 2. Streamlit Community Cloud にログインする

[https://share.streamlit.io/](https://share.streamlit.io/)

### 3. 新しいアプリを作る

設定の目安:

- Repository: GitHub の対象リポジトリ
- Branch: `main`
- Main file path: `app.py`

### 4. デプロイする

`Deploy` を押します。

### 5. データファイルを確認する

Community Cloud では、リポジトリに含まれる `data/` 配下の CSV を読みます。
最初はサンプルデータで動作確認できます。

## 今後の拡張予定

- J-Quants からの上場企業マスター更新
- `hokendb` の実取得ロジック追加
- 日本年金機構の本線 collector 追加
- 法人番号ベースの厳密マッチング
- 監査ワークフローの強化

## 注意

このアプリは投資判断を目的としたものではありません。
`hokendb` 等から取得したデータには、欠損・揺れ・誤マッチの可能性があります。
そのため、`match_status` と `quality_flag` を必ず確認してください。
