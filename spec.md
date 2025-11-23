MSAR-Lite “Best Design” 設計書 v1.2.1（Codex投入用・A/B/C反映）

0. 目的
UK/EU配信の静止画広告を公式Ad Library APIで日次収集し、
coarse概念タグの急増/継続を抽象化して“今日の勝ち型BEST3”を1ページで提示する。

1. スコープ
1.1 In Scope
Ad Library API（/ads_archive）から日次取得
取得戦略：Guarantee（PageID主導）＋Explore（search_terms補助）
Explore→新規PageID発掘→Guaranteeへ昇格する運用ループ
ノイズ除外
画像DL（fetch直後、snapshot再生成、秒でDL）
重複排除（text hash / pHash / 補助一致）
画像/テキスト特徴抽出（LLMなし）
coarseタグ生成（color×person×layout）
日次freq、Rate、Persistence、CountScore
推定impressions取得時のみImprScore補助（レンジ数値化規約あり）
BEST3、急増TOP5、要素別ランキング出力
静的HTML 1ページ生成
日次バッチ運用、再試行、フェイルセーフ、監視、アラート
1.2 Out of Scope
成果推定（CVR/ROAS/CPA等）
動画広告解析
Embedding/LLM抽象
マルチテナントSaaS、課金、ユーザー管理
リアルタイム更新

2. 制約（前提）
APIは検索APIで search_terms または search_page_ids 必須。全量ダンプ不可。
UK/EU商用のimpressionsは 推定値かつレンジ（バケット）表現の可能性が高いため、数値化規約を固定する。
snapshot_urlはTTL短い署名URLになり得るため、fetchと画像DLは同一ランで直結（後回し禁止）。
LLM/有料Vision不使用。

3. 全体アーキテクチャ（即DL強制）
Ad Library API (UK/EU)        |  [1] fetch_meta.py (Guarantee + Explore)        |    （同一ラン・即時）        |  [2] download_images.py (snapshot再生成, 秒でDL)        |  [3] filter_noise.py        |  [4] dedupe.py        |  [5] extract_features.py        |  [6] tagger.py (coarse)        |  [7] trend.py (Count主 + Impr補助)        |  [8] render_html.py        |  MySQL + index.html 
※ download_images は run_daily から fetch直後に同期呼び出し。
 非同期化する場合も キュー投入はfetch直後に必須、別バッチ化は禁止。

4. リポジトリ/モジュール構成
src/   config.py   run_daily.py    fetch_meta.py     - GuaranteeFetcher     - ExploreFetcher     - MockFetcher    download_images.py   filter_noise.py   dedupe.py   extract_features.py   tagger.py   trend.py   render_html.py    db.py   utils/     cv_utils.py     ocr_utils.py     phash_utils.py     text_utils.py     logging_utils.py  migrations/ docker/ requirements.txt data/   dicts/   explore_terms.txt   guarantee_page_ids.txt 

5. データ取得仕様（A反映）
5.1 GuaranteeFetcher（主経路：再現性）
対象国：UK/EU
入力：guarantee_page_ids.txt に列挙された Page ID 群
複数Page IDを1リクエストで指定可能な範囲で最大化して送る。
API制限を超える場合は Page IDをバッチ分割して複数リクエスト。
取得件数：日次の7–9割をGuaranteeで確保する目標
出力：ads_raw配列（ad_id一意化前）
5.2 ExploreFetcher（補助線：スカウト）
対象国：UK/EU
入力：explore_terms.txt の小セット（10–30語）
目的：Coverage補助 ＋ 新規有力Page IDの発掘
取得後、探索結果から“有力Page ID候補”を抽出して昇格候補リスト化する。
5.2.1 Page ID 昇格フロー（運用仕様）
Exploreで得た広告の page_id を日次集計し、
page_freq_7d（直近7日での出現ユニーク広告数）
page_recency（最終出現日）
 を計算。
条件を満たすPageを promotion_candidates として生成：
page_freq_7d >= P_MIN（例：5）
page_recency <= 2days
promotion_candidates は run_log に保存。
人手（または後の自動化）で guarantee_page_ids.txt に追記→翌日からGuaranteeに入る。

6. snapshot即DL仕様（C反映）
6.1 snapshot再生成
APIレスポンスの snapshot_url を 保存せず、
 render_ad?id={ad_id}&access_token={token} で毎回再生成する。
6.2 即DL強制
fetch_meta 完了直後に download_images を同一ラン内で実行。
fetchからDL開始までの待機は禁止（秒オーダーで開始）。
DL失敗は3回指数バックオフ、最終失敗で invalid_media。

7. ノイズ除外（filter_noise）
除外：
ad_id欠落
body/title/description全空
画像DL失敗
OCR 0文字 or 異常過多
画像破損/比率異常
指標：
N_fetched, N_valid
N_valid < 40 → is_reference=true

8. 重複排除（dedupe）
3段階統合：
text_hash完全一致
pHash距離 < τ（初期τ=5）
補助一致（dominant_color一致＋OCR上位語一致）
結果：
ads_unique
N_unique

9. 特徴抽出（extract_features）
dominant_color：HSVクラスタ→5色
person_bucket：MediaPipe顔検出 0/1/multi
text_amount_bucket：OCR文字数 small/medium/big
layout_bucket：OCR bbox縦分布
cta_present：CTA regex/fuzzy辞書
number_density_bucket：数字比率 high/low
OCR前処理必須（resize→gray→CLAHE→bilateral→adaptive thr→morph close→2pass OCR）。

10. タグ生成（tagger）
coarse固定：
 concept_tag = {color}×{person}×{layout}

11. Trend/Score（B反映）
11.1 CountScore（主）
freq = unique_ads_count(tag) rate = (freq_today - freq_yesterday) / (freq_yesterday + 1) persistence = ma3_today / (ma3_yesterday + 1) count_score = rate + persistence 
11.2 Impressionsの数値化規約
APIが返すimpressionsがレンジ表現の場合、
 impr_range_raw を保存し、impr_value を規約で決定。
規約（固定）：
"0-1000" → 500（中央値）
"1000-5000" → 3000（中央値）
"5000-10000" → 7500
"10000+" → 10000（下限）
単一値の場合はそのまま採用
欠落/nullは impr_value=null
11.3 ImprScore（補助）
impr_available_ratio >= θ の日だけ有効。
impr_today = sum(impr_value(tag)) impr_rate = (impr_today - impr_yesterday) / (impr_yesterday + 1) impr_score = impr_rate + persistence 
11.4 BEST3 / TOP5
BEST3：
impr_available_ratio >= θ → impr_score優先
それ以外 → count_score
TOP5：rate順
併記：要素別ランキング（color/person/layout単体のrate）

12. 出力HTML（render_html）
静的1ページ。
表示：
BEST3（タグ＋採用スコアタイプ＋短文化テンプレ）
急増TOP5
要素別急増ランキング
N_valid / N_unique / explore_ratio / impr_available_ratio
注記（参考値/前日再掲/取得障害）

13. DBスキーマ
ads_raw
id, fetch_date
ad_id
page_id, page_name
body, title, description
reached_countries
status (fetched/invalid)
ads_unique
id, fetch_date, ad_id, page_id
image_path
text_hash, phash
dominant_color, person_bucket, text_amount_bucket, layout_bucket
cta_present, number_density_bucket
concept_tag
features_json
concept_daily
id, date, concept_tag
freq, rate, persistence
count_score
impr_range_raw (nullable)
impr_value (nullable)
impr_rate (nullable)
impr_score (nullable)
score_selected_type (count/impr)
run_log
id, date
N_fetched, N_valid, N_unique
guarantee_count, explore_count, explore_ratio
empty_rate
impr_available_ratio
promotion_candidates_json  // PageID昇格候補
step_status_json
error_summary
is_reference

14. 運用・フェイルセーフ（run_daily）
各ステップ最大3回リトライ（指数バックオフ）
最終失敗日：concept_daily前日コピー、HTML前日再掲＋注記
監視：explore_ratio急増 / empty_rate上昇 / impr_available_ratio低下

15. DoD
稼働：
7日連続でバッチ停止なし
毎日BEST3/TOP5/母数が出る
失敗日も前日再掲＋注記でUI成立
価値：
 4. Guarantee主の日でもBEST3が変動する
 5. 要素別ランキングが連日で傾向を示す

16. 実装優先順（Codex指示）
migrations
MockFetcher＋run_daily骨格
GuaranteeFetcher（複数PageIDバッチ送信）
fetch直後の即DL（同期）
filter_noise → dedupe
extract_features（HSV/Face/OCR前処理）
tagger（coarse）
trend（Count主＋Imprレンジ数値化＋補助）
render_html
PageID昇格候補の生成/ログ化

