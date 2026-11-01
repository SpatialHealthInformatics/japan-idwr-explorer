# =============================================================================
# i18n.py: English / Japanese (日本語) switch for the Japan Surveillance Explorers
# Author:   Genie Tang (gtang10@jh.edu)
# Version:  v1
#
# How it works: app.py keeps its English text. When the sidebar language is 日本語,
# this module translates text on its way to the page (labels, markdown, tables,
# chart titles and hover text). English is the default and is never changed.
# Open the Japanese version directly with ?lang=ja at the end of the app address.
# To add or fix a Japanese phrase, edit DATA below (english text -> japanese text).
# =============================================================================
import functools
import re

import streamlit as st
from streamlit.delta_generator import DeltaGenerator as _DG

DATA = {
"exact": {
"Hokkaido": "北海道",
"Tohoku": "東北",
"Kanto": "関東",
"Chubu": "中部",
"Kinki (Kansai)": "近畿（関西）",
"Chugoku": "中国",
"Shikoku": "四国",
"Kyushu": "九州",
"Okinawa": "沖縄",
"Influenza": "インフルエンザ",
"Epidemic": "流行",
"Caution": "注意報",
"Warning": "警報",
"COVID-19": "新型コロナウイルス感染症（COVID-19）",
"RSV infection": "RSウイルス感染症",
"Group A streptococcal pharyngitis": "A群溶血性レンサ球菌咽頭炎",
"Herpangina": "ヘルパンギーナ",
"Mycoplasma pneumonia": "マイコプラズマ肺炎",
"Under 1.0": "1.0未満",
"30.0 and over": "30.0以上",
"High-High": "高-高",
"Low-Low": "低-低",
"High-Low": "高-低",
"Low-High": "低-高",
"Not significant": "有意でない",
"All Japan": "日本全体",
"Kanto (Tokyo area)": "関東（東京周辺）",
"Kansai (Osaka area)": "関西（大阪周辺）",
"not rated": "対象外",
"Okinawa (inset)": "沖縄（挿入図）",
"IDWR levels": "IDWR区分",
"per sentinel": "定点あたり",
"Yes": "はい",
"Prefecture": "都道府県",
"Reports per sentinel": "定点あたり報告数",
"Sentinel sites": "定点数",
"Alert": "アラート",
"Population (2020)": "人口（2020年）",
"Japan IDWR Surveillance Explorer": "日本 IDWRサーベイランス・エクスプローラー",
"Prefectures": "都道府県",
"Add a prefecture": "都道府県を追加",
"Type or pick a prefecture": "都道府県を入力または選択",
"Add": "追加",
"Selected prefectures (click x to remove)": "選択中の都道府県（×で削除）",
"Display options": "表示オプション",
"Disease": "疾患",
"IDWR week (maps and cards)": "IDWR週（地図とカード）",
"Weeks shown (charts)": "表示する週（グラフ）",
"Chart layout": "グラフの配置",
"One chart": "1つのグラフ",
"One panel per prefecture": "都道府県ごとにパネル",
"Mark C2 alerts on the chart": "グラフにC2アラートを表示",
"Log scale (y-axis)": "対数目盛（縦軸）",
"Leave New Year weeks out of C2 baselines": "年末年始の週をC2基準期間から除外",
"Weekly IDWR Reports by Prefecture in Japan": "日本の都道府県別週次IDWR報告",
"Spatial Statistics": "空間統計",
"Chart": "グラフ",
"Prefecture Map": "都道府県マップ",
"Japan Map": "日本マップ",
"Alerts": "アラート",
"Summary Table": "集計表",
"User Guide": "使い方",
"About the Data": "データについて",
"Global Moran's I": "全体のモランI",
"Permutation p-value": "順列検定のp値",
"High-High prefectures": "高-高の都道府県",
"Prefectures in analysis": "解析対象の都道府県",
"Similar levels sit together": "似た水準が隣り合っている",
"No clear spatial pattern": "明確な空間パターンなし",
"Standardized reports per sentinel (z)": "標準化した定点あたり報告数（z）",
"Spatial lag of z (neighbors' mean)": "空間ラグ（隣接都道府県の平均のz）",
"**Moran scatterplot**": "**モラン散布図**",
"top left": "左上",
"Download the plotted data (CSV)": "表示データをダウンロード（CSV）",
"Area": "地域",
"Kanto and Kansai": "関東と関西",
"Shade prefectures by": "都道府県の色分け",
"Continuous": "連続",
"Outline prefectures with a C2 alert this week (black)": "今週C2アラートが出た都道府県を枠線で表示（黒）",
"Region of each selected prefecture": "選択した都道府県の地域",
"Map style": "地図の種類",
"Shaded": "色分け",
"Bubbles": "バブル",
"Alert threshold (standard deviations above baseline)": "アラートのしきい値（基準より何標準偏差上か）",
"Alert weeks in window": "期間内のアラート週数",
"Weeks in window": "期間内の週数",
"First alert": "最初のアラート",
"Largest C2": "C2の最大値",
"Week of largest C2": "C2が最大の週",
"Below 1.0, then crossed": "1.0未満から上昇",
"Pending": "判定保留",
"Reports per sentinel, ": "定点あたり報告数、",
"Peak": "ピーク",
"Alert weeks": "アラート週数",
"Table shows": "表示対象",
"All 47 prefectures": "全47都道府県",
"Selected prefectures": "選択した都道府県",
"Lead (weeks)": "リード（週）",
"Peak week": "ピーク週",
"Onset (sustained 1.0)": "流行開始（1.0を継続して上回る）",
"First C2 alert": "最初のC2アラート",
"Reached 1.0": "1.0に到達",
"Alert came first": "アラートが先行",
"Median lead": "リードの中央値",
"No prefecture with a lead": "リードのある都道府県なし",
"False alarms": "誤警報",
"Japan Influenza Surveillance Explorer": "日本 インフルエンザ サーベイランス・エクスプローラー",
"Weekly Influenza Reports by Prefecture in Japan": "日本の都道府県別 週次インフルエンザ報告"
},
"frag": {
"This app uses public IDWR data only. The TriNetX data used in the JSPID comparison is not included, because it is not public data. If it becomes available for sharing, it will be added here.": "本アプリは公開されているIDWRデータのみを使用しています。JSPIDでの比較に用いたTriNetXデータは、公開データではないため含まれていません。共有が可能になった場合は、ここに追加します。",
"Public IDWR data only. The TriNetX comparison is not included.": "IDWRの公開データのみ。TriNetXとの比較は含まれていません。",
"Sentinel scheme changed in April 2025, when acute respiratory infection (ARI) surveillance began and the number of sentinel sites fell. Trends need care, because the size of the gap between the old and new systems is not yet clear.": "2025年4月に急性呼吸器感染症（ARI）サーベイランスが始まり、定点医療機関の数が減少しました。新旧の制度間の差の大きさはまだ明らかではないため、推移の解釈には注意が必要です。",
"Pediatric sentinel scheme, not part of the April 2025 ARI change. To be confirmed with JIHS.": "小児科定点の枠組みであり、2025年4月のARI制度変更の対象ではありません。JIHSに確認予定です。",
"Sentinel scheme not yet checked for this disease.": "この疾患の定点の枠組みは、まだ確認していません。",
"Small outlying islands are left off the maps (for example Ogasawara and Amami); Okinawa is shown in the inset box.": "小さな離島（小笠原や奄美など）は地図から除いています。沖縄は挿入図に表示しています。",
"Loading IDWR weekly reports...": "IDWR週次報告を読み込み中...",
" rows with codes outside 1 to 47 were dropped (": "件の行は、都道府県コードが1〜47の範囲外のため除外しました（",
"Names differ from the code list for codes ": "コード表と名称が異なるコード：",
"; the code list names are used.": "。コード表の名称を使用します。",
" prefectures have no rows: ": "都道府県にデータ行がありません：",
"Running Moran's I and LISA...": "モランIとLISAを計算中...",
"Running Moran's I for every week...": "各週のモランIを計算中...",
"SAMPLE DATA, NOT REAL": "サンプルデータ（実データではありません）",
"<b>%{text}</b><br>Reports per sentinel: %{customdata[0]:.2f}": "<b>%{text}</b><br>定点あたり報告数：%{customdata[0]:.2f}",
"<br>Sentinel sites: %{customdata[3]}": "<br>定点数：%{customdata[3]}",
"<br>C2: %{customdata[1]:.1f}<br>Alert: %{customdata[2]}<extra></extra>": "<br>C2：%{customdata[1]:.1f}<br>アラート：%{customdata[2]}<extra></extra>",
"<b>%{text}</b><br>Reports per sentinel: %{customdata:.2f}<extra></extra>": "<b>%{text}</b><br>定点あたり報告数：%{customdata:.2f}<extra></extra>",
"⟲  Reset map view": "⟲地図の表示を戻す",
"Zoom back out to the starting view": "最初の表示に戻す",
"Use + and − at the top right of the map to zoom, and drag to move. Press Reset map view to return to the starting view.": "地図右上の＋と−で拡大縮小し、ドラッグで移動できます。「地図の表示を戻す」を押すと最初の表示に戻ります。",
"'>Reports per sentinel site": "'>定点あたり報告数",
"The weekly IDWR table is not loaded yet. Add data/idwr_weekly.csv, written by the IDWR alert report R script, and reload the page.": "週次IDWR表がまだ読み込まれていません。IDWRアラートレポート用Rスクリプトが出力する data/idwr_weekly.csvを追加して、ページを再読み込みしてください。",
"Could not read the weekly IDWR table: ": "週次IDWR表を読み込めませんでした：",
"Tokyo": "東京",
"Osaka": "大阪",
"Nara": "奈良",
" prefectures can be compared at once. Remove one first.": "都道府県まで同時に比較できます。先にどれかを削除してください。",
"Most prefecture weeks have almost no reports for this disease, so C2 alerts are not reliable.": "この疾患は、ほとんどの都道府県・週で報告がほぼないため、C2アラートは信頼できません。",
"The 1.0 level, onset, lead time and false alarms apply to influenza only. The minimum SD of 0.1 was set for influenza and has not been tested for this disease.": "1.0の基準、流行開始、リードタイム、誤警報はインフルエンザにのみ適用されます。最小SD 0.1はインフルエンザ用に設定したもので、この疾患では検証していません。",
"Weeks run Monday to Sunday.": "週は月曜日から日曜日までです。",
"Separate panels help when one prefecture's values dwarf the others.": "1つの都道府県の値が他より極端に大きい場合は、パネルを分けると見やすくなります。",
"Clinic closures around New Year lower reports in weeks 52, 53 and 1. On by default. Turn off to use every week, as the R alert report does now.": "年末年始の休診により、52週・53週・1週の報告数が減ります。初期設定はオンです。オフにすると、現在のRアラートレポートと同じく、すべての週を使います。",
"SAMPLE DATA. These are synthetic values for layout only, not IDWR reports.": "サンプルデータです。レイアウト確認用の合成値であり、IDWRの報告ではありません。",
" (SAMPLE DATA)": "（サンプルデータ）",
"<p style='opacity:0.78; font-size:1.05rem; margin-top:-0.4rem'>Pick prefectures in the sidebar and compare reports per sentinel site by week, with EARS C2 alerts and spatial clustering. Source: Japan Institute for Health Security, Infectious Disease Weekly Report (<a href='": "<p style='opacity:0.78; font-size:1.05rem; margin-top:-0.4rem'>サイドバーで都道府県を選び、定点あたり報告数を週ごとに比較できます。EARS C2アラートと空間クラスタリングも表示します。出典：国立健康危機管理研究機構（JIHS）、感染症発生動向調査週報（<a href='",
"'>IDWR</a>). App ": "'>IDWR</a>）。アプリ",
"**Sample data, not real.** Every number, chart and map on this page comes from a synthetic file made for layout. Nothing here describes disease in Japan. Load data/idwr_weekly.csv from the R script before sharing or deploying.": "**サンプルデータであり、実データではありません。** このページのすべての数値、グラフ、地図は、レイアウト確認用の合成ファイルによるものです。日本の疾患の状況を表すものではありません。共有または公開の前に、Rスクリプトが出力する data/idwr_weekly.csvを読み込んでください。",
"Geography check: ": "地理情報の確認：",
"**Do prefectures with high ": "**",
" reports sit next to each other?** Global Moran's I measures that for the whole country; local Moran (LISA) finds the clusters.": "の報告が多い都道府県は、互いに隣り合っているか？** 全体のモランIは国全体でそれを調べ、局所モラン（LISA）はクラスターを特定します。",
" has missing or identical values, so spatial statistics are not computed.": "は欠測または同一の値のため、空間統計を計算していません。",
"<br>Near 0 would mean no pattern": "<br>0に近いほど、パターンなし",
" random re-assignments<br>of the values to prefectures": "回のランダムな入れ替え<br>（値を都道府県に再割り当て）",
"High reports whose neighbors<br>also have high reports": "高い報告数で、隣接する都道府県<br>も高い報告数",
"Week ": "週：",
"<br>Border neighbors plus 3 sea links": "<br>隣接する都道府県と海を越えた3つの接続",
"<br>Reports per sentinel: %{customdata[0]:.2f}<br>p = %{customdata[1]:.3f}<extra></extra>": "<br>定点あたり報告数：%{customdata[0]:.2f}<br>p = %{customdata[1]:.3f}<extra></extra>",
"**LISA clusters** · reports per sentinel site · ": "**LISAクラスター** ·定点あたり報告数 · ",
" · p below 0.05": " · p 0.05未満",
". Selected prefectures are outlined in orange. ": "。選択した都道府県はオレンジ色の枠で示しています。",
"<b>%{text}</b><br>z = %{x:.2f}<br>spatial lag = %{y:.2f}<extra></extra>": "<b>%{text}</b><br>z = %{x:.2f}<br>空間ラグ = %{y:.2f}<extra></extra>",
"Slope = Moran's I (": "傾き =モランI（",
"%{customdata[0]}<br>I = %{y:.2f}<br>p = %{customdata[1]:.3f}<extra></extra>": "%{customdata[0]}<br>I = %{y:.2f}<br>p = %{customdata[1]:.3f}<extra></extra>",
"**Global Moran's I by week** · orange points: p below 0.05 · gray line: map week": "**週ごとの全体のモランI** ·オレンジの点：p 0.05未満 ·灰色の線：地図の週",
"Method: reports per sentinel site for the map week. Spatial weights: prefectures that share a border (queen contiguity on the full-resolution boundaries), plus Hokkaido-Aomori and Okinawa-Kagoshima (nearest prefecture by distance) and Fukuoka-Yamaguchi (Kanmon Strait), row-standardized. Global Moran's I and local Moran from PySAL esda with ": "方法：地図の週の定点あたり報告数を使用。空間重み：境界を共有する都道府県（クイーン隣接、高解像度の境界）に、北海道-青森と沖縄-鹿児島（距離で最も近い都道府県）、福岡-山口（関門海峡）を加え、行基準化しています。全体のモランIと局所モランはPySALのesdaで、",
" permutations. Expected I under no spatial pattern: ": "回の順列検定を用いて計算しました。空間パターンがない場合の期待値I：",
". High-High: a high-reporting prefecture with high-reporting neighbors; Low-Low: the reverse; High-Low and Low-High are spatial outliers. Sentinel reports reflect care-seeking and reporting practice, so the clusters describe the reported data.": "。高-高：報告の多い都道府県が、報告の多い都道府県に隣接。低-低：その逆。高-低と低-高は空間的な外れ値です。定点の報告は受診行動や報告の実態を反映するため、クラスターは報告されたデータの特徴を表します。",
"Install libpysal and esda (see requirements.txt) to enable this tab.": "このタブを使うには、libpysalとesdaをインストールしてください（requirements.txtを参照）。",
"Add at least one prefecture in the sidebar to see the chart.": "グラフを表示するには、サイドバーで都道府県を1つ以上追加してください。",
"</div><div class='sub'>No values in this window.</div></div>": "</div><div class='sub'>この期間に値はありません。</div></div>",
"</div><div class='sub'>Reports per sentinel in ": "</div><div class='sub'>定点あたり報告数 ",
"<br>Peak ": "<br>ピーク ",
" C2 alert weeks in window</div></div>": "週のC2アラート（期間内）</div></div>",
"C2 alert (C2 = %{customdata:.1f})<extra>": "C2アラート（C2 = %{customdata:.1f}）<extra>",
": reports per sentinel site by week** · ": "：定点あたり報告数（週別）** · ",
"Hover for every prefecture's value in a week. Diamonds mark EARS C2 alerts. Dashed line: epidemic threshold (1.0). Dotted lines: caution (10) and warning (30). Drag on the chart to zoom; double-click to reset. Log scale hides weeks with zero reports.": "グラフ上にカーソルを合わせると、その週の全都道府県の値を表示します。ひし形はEARS C2アラートです。破線：流行の基準（1.0）。点線：注意報（10）と警報（30）。グラフはドラッグで拡大、ダブルクリックで元に戻ります。対数目盛では報告ゼロの週は表示されません。",
"Five bands: under 1.0, then 1.0 to 9.99, 10 to 19.99, 20 to 29.99, and 30 and over.": "5段階：1.0未満、1.0〜9.99、10〜19.99、20〜29.99、30以上。",
"Add prefectures in the sidebar; each one appears as a bubble on a map of its region.": "サイドバーで都道府県を追加すると、各都道府県がその地域の地図上にバブルで表示されます。",
"**Region of each selected prefecture** · bubble area shows reports per sentinel site · ": "**選択した都道府県の地域** ·バブルの面積は定点あたり報告数 · ",
" per sentinel · C2 ": "定点あたり · C2 ",
" · **alert**": " · **アラート**",
"** · reports per sentinel site · ": "** ·定点あたり報告数 · ",
"Each map shows one region; a bubble marks each selected prefecture in its chart color, sized by reports per sentinel site on one scale for all maps. The shading options apply to the Kanto and Kansai views. Hover any prefecture for its value.": "各地図は1つの地域を表示します。選択した都道府県ごとに、グラフと同じ色のバブルを描き、面積はすべての地図で共通の尺度で定点あたり報告数を表します。色分けの設定は関東と関西の表示に適用されます。都道府県にカーソルを合わせると値を表示します。",
"Prefectures outside the area are faded. Selected prefectures are outlined in bright blue": "対象地域外の都道府県は薄く表示しています。選択した都道府県は明るい青の枠で示しています",
"; prefectures with a C2 alert this week in black": "。今週C2アラートが出た都道府県は黒で示しています",
". Hover any prefecture for its numbers, including C2 and whether it alerted.": "。都道府県にカーソルを合わせると、C2とアラートの有無を含む数値を表示します。",
"Prefectures shown here ranked by reports per sentinel, ": "ここに表示した都道府県を定点あたり報告数順に並べています（",
"Shaded: every prefecture colored by its level. Bubbles: a gray map with a bubble for each selected prefecture, sized by reports per sentinel site.": "色分け：すべての都道府県を水準に応じて着色します。バブル：灰色の地図に、選択した都道府県ごとのバブルを表示し、面積は定点あたり報告数です。",
": selected prefectures** · reports per sentinel site · ": "：選択した都道府県** ·定点あたり報告数 · ",
"Bubble area shows reports per sentinel site, on one scale for all prefectures, in each selected prefecture's chart color. Add prefectures in the sidebar to add bubbles. ": "バブルの面積は定点あたり報告数で、すべての都道府県で共通の尺度です。色は各都道府県のグラフの色と同じです。サイドバーで都道府県を追加するとバブルが増えます。",
": reports per sentinel site in every prefecture** · ": "：全都道府県の定点あたり報告数** · ",
"Five bands: under 1.0, then steps up to the warning level of 30. ": "5段階：1.0未満から、警報の30まで段階的に上がります。",
"One warm scale from cream to dark red; the darkest step starts at the 98th percentile of the season (": "クリーム色から濃い赤へ向かう1つの暖色の尺度で、最も濃い色はシーズンの98パーセンタイル（",
") so a few extreme values do not flatten the rest. ": "）から始まります。少数の極端な値で全体が平坦に見えないようにするためです。",
"Labels show the 8 highest prefectures, your selected prefectures and Okinawa. ": "ラベルには、上位8都道府県、選択した都道府県、沖縄を表示します。",
"Selected prefectures are outlined in bright blue": "選択した都道府県は明るい青の枠で示しています",
"; prefectures with a C2 alert this week in black. ": "。今週C2アラートが出た都道府県は黒で示しています。",
"All prefectures ranked by reports per sentinel, ": "全都道府県を定点あたり報告数順に並べています（",
"**When would a surveillance system have raised an alert?** EARS C2 compares each week's reports per sentinel with the mean and standard deviation of weeks t-9 to t-3, leaving a two-week guard (t-2 and t-1). A week that many standard deviations above that baseline is an alert.": "**サーベイランスはいつアラートを出せたか？** EARS C2は、各週の定点あたり報告数を、t-9〜t-3週の平均と標準偏差と比べます（t-2とt-1は2週間のガード）。基準より標準偏差が何倍も高い週がアラートです。",
"Add at least one prefecture in the sidebar to see the alerts.": "アラートを表示するには、サイドバーで都道府県を1つ以上追加してください。",
"Alert: %{y:.2f} (C2 = %{customdata:.1f})<extra></extra>": "アラート：%{y:.2f}（C2 = %{customdata:.1f}）<extra></extra>",
"**Reports per sentinel site with EARS C2 alerts** · threshold ": "**EARS C2アラート付きの定点あたり報告数** ·しきい値 ",
"**New Year check, all 47 prefectures, ": "**年末年始の確認（全47都道府県、",
".** Alert weeks in weeks 2 to 8: ": "）。** 2〜8週のアラート週数：",
" with weeks 52, 53 and 1 kept in the baselines, ": "（52・53・1週を基準期間に含めた場合）、",
" with them left out. This page uses the ": "（除外した場合）。このページでは",
"Method: EARS C2 (CDC Early Aberration Reporting System). Baseline = the 7 weeks ending three weeks before the week being tested (t-9 to t-3), leaving a two-week guard (t-2 and t-1). C2 = (reports per sentinel - baseline mean) / baseline SD, using the population SD with a floor of 0.1 and at least 5 baseline weeks. These are the same rules as the IDWR alert report R script.": "方法：EARS C2（CDCの早期異常検知システム）。基準期間は、検査する週の3週前までの7週間（t-9〜t-3）で、t-2とt-1は2週間のガードです。C2 =（定点あたり報告数 −基準期間の平均）／基準期間のSD。SDは母集団SDで、下限を0.1とし、基準期間は5週以上が必要です。IDWRアラートレポートのRスクリプトと同じルールです。",
" Dashed line: epidemic threshold, 1.0. A false alarm is an alert below 1.0 with no week at 1.0 or above in that week or the next ": "破線：流行の基準、1.0。誤警報とは、1.0未満のアラートのうち、その週と以降",
"; pending means fewer than ": "週のあいだに1.0以上の週がなかったものです。判定保留とは、追跡期間が",
" weeks of follow-up so far.": "週に満たないものです。",
" The 1.0 level, false alarms and lead times apply to influenza only, so they are not shown for this disease.": " 1.0の基準、誤警報、リードタイムはインフルエンザにのみ適用されるため、この疾患では表示しません。",
" (set with Weeks shown in the sidebar). The four cards (influenza only) summarize all 47 prefectures.": "（サイドバーの「表示する週」で設定）。4つのカード（インフルエンザのみ）は全47都道府県を集計しています。",
"Onset, lead time and false alarms use the influenza 1.0 level, so they are shown for influenza only.": "流行開始、リードタイム、誤警報はインフルエンザの1.0の基準を使うため、インフルエンザのみ表示します。",
" selected in the sidebar; click a column header to sort.": "件を選択中（サイドバー）。列見出しをクリックすると並べ替えできます。",
"No prefectures selected. Add prefectures in the sidebar, or choose All 47.": "都道府県が選択されていません。サイドバーで追加するか、「全47都道府県」を選んでください。",
"All 47 prefectures; click a column header to sort.": "全47都道府県。列見出しをクリックすると並べ替えできます。",
"Reports per sentinel site<br>of 1.0 or more in these weeks": "この期間に定点あたり報告数<br>1.0以上となった都道府県",
"First C2 alert before<br>the onset week": "最初のC2アラートが<br>流行開始の週より前",
"Alerts below 1.0 with no crossing<br>in the next ": "1.0未満のアラートのうち、<br>以降 ",
"Weeks the first C2 alert came before onset. 0 means the same week; a negative number means the alert came after onset.": "最初のC2アラートが流行開始より何週前だったか。0は同じ週、負の数はアラートが流行開始より後だったことを示します。",
"Onset = the first week of the unbroken run at or above 1.0 per sentinel that contains the peak. First C2 alert = the first alert from ": "流行開始＝ピークを含む、定点あたり1.0以上が途切れず続いた期間の最初の週。最初のC2アラート＝流行開始の",
" weeks before the onset onward; earlier alerts count toward false alarms. Lead = onset week minus first alert week; positive means the alert came first. Blank when C2 had too little history before the onset.": "週前以降で最初のアラート。それより前のアラートは誤警報に数えます。リード＝流行開始週−最初のアラート週で、正の値はアラートが先行したことを示します。流行開始前にC2の履歴が足りない場合は空欄です。",
"the c2 column written by the R alert report": "Rアラートレポートが出力したc2列",
"C2 computed in this app with the R alert report's rules": "本アプリでRアラートレポートと同じルールにより計算したC2",
", New Year weeks left out of baselines": "、年末年始の週を基準期間から除外",
"Every year-week label matches the ISO week of its start date.": "年週ラベルはすべて、開始日のISO週と一致しています。",
" week labels do not match the ISO week of their start date; check how IDWR numbers weeks in 53-week years.": "件の週ラベルが、開始日のISO週と一致しません。IDWRが53週ある年の週番号をどう付けているか確認してください。",
"All 47 prefectures are present, with the expected names.": "47都道府県がすべてそろっており、名称も想定どおりです。",
"SAMPLE DATA. Synthetic values for layout only. No real surveillance values are shown.": "サンプルデータです。レイアウト確認用の合成値のみで、実際のサーベイランス値は表示していません。",
"IDWR reports per sentinel site for all 47 prefectures, ": "全47都道府県の定点あたり報告数（IDWR）、",
", from the prefecture table written by the IDWR alert report R script. C2 starts 9 weeks into the table, because each week needs 9 earlier weeks for its baseline and guard.": "、IDWRアラートレポート用Rスクリプトが出力した都道府県表より。C2は、各週に基準期間とガード用の過去9週が必要なため、表の9週目から始まります。",
"\n**Getting started**\n1. In the sidebar, pick a prefecture in **Add a prefecture** and press **Add**. You can also type straight into\n   **Selected prefectures**. Remove a prefecture with the **x** on its tag. Up to six prefectures can be compared\n   at once; each keeps its color while selected.\n2. Move **IDWR week** to choose the week shown on the maps, the spatial statistics and the summary table.\n3. Drag **Weeks shown** to choose the period on the chart and the alerts.\n4. **One panel per prefecture** gives each prefecture its own panel, which helps when one prefecture's values\n   dwarf the others. **Log scale** is another way to handle that.\n5. **Leave New Year weeks out of C2 baselines** is on by default. Turn it off to use every week, as the R alert\n   report does now. The Alerts tab shows how many alerts in weeks 2 to 8 each rule gives.\n\n**Reading the results**\n- **Spatial Statistics** tests whether high-reporting prefectures sit next to each other (global Moran's I),\n  maps the clusters (LISA), and shows Moran's I for every week, so you can see clusters form through a season.\n- **Chart**: the tiles show each prefecture's latest value in the window, its peak, and the number of alert\n  weeks. The dashed line is the epidemic threshold (1.0); the dotted lines are the caution (10) and warning (30)\n  levels.\n- **Prefecture Map** shows Kanto and Kansai side by side, one of them, or only your selected prefectures, with\n  the rest of Japan faded. **Japan Map** shades all 47 prefectures and ranks them in a table below. Both offer\n  the five IDWR color bands or a continuous scale.\n- **Alerts** runs EARS C2 on each selected prefecture and marks the weeks a surveillance system would have raised\n  an alert. Move the threshold slider to see how the count changes.\n- **Summary Table** gives, for the selected prefectures or all 47, each prefecture's peak, its onset week (sustained 1.0), its first C2 alert, the lead\n  between them, and the number of false alarms next to the lead.\n- **Download the plotted data** saves exactly what is on the chart as a CSV file.\n": "\n**はじめに**\n1. サイドバーの **都道府県を追加** で都道府県を選び、**追加** を押します。**選択中の都道府県** に直接入力することもできます。\n   削除するには、タグの **×** を押します。同時に比較できるのは最大6都道府県で、選択中は色が保たれます。\n2. **IDWR週** で、地図、空間統計、集計表に表示する週を選びます。\n3. **表示する週** をドラッグして、グラフとアラートの期間を選びます。\n4. **都道府県ごとにパネル** は、都道府県ごとに別のパネルを表示します。1つの都道府県の値が他より極端に大きいときに便利です。\n   **対数目盛** も同じ目的に使えます。\n5. **年末年始の週をC2基準期間から除外** は、初期設定でオンです。オフにすると、現在のRアラートレポートと同じく、すべての週を使います。\n   アラートタブで、2〜8週のアラート数が各ルールでどう変わるかを確認できます。\n\n**結果の見方**\n- **空間統計**：報告の多い都道府県が隣り合っているかを検定し（全体のモランI）、クラスターを地図に示し（LISA）、\n  各週のモランIも表示するため、シーズン中にクラスターができていく様子を見られます。\n- **グラフ**：タイルに、期間内の各都道府県の最新値、ピーク、アラート週数を表示します。破線は流行の基準（1.0）、\n  点線は注意報（10）と警報（30）の水準です。\n- **都道府県マップ**：関東と関西を並べて、またはどちらか一方、あるいは選択した都道府県だけを表示し、他の地域は薄く表示します。\n  **日本マップ**：全47都道府県を色分けし、下の表に順位を示します。どちらも、IDWRの5段階の色分けか連続尺度を選べます。\n- **アラート**：選択した各都道府県にEARS C2を適用し、サーベイランスがアラートを出せた週を示します。\n  しきい値のスライダーを動かすと、件数がどう変わるかを確認できます。\n- **集計表**：選択した都道府県または全47都道府県について、ピーク、流行開始週（1.0を継続して上回る）、最初のC2アラート、\n  その間のリード、誤警報数を示します。\n- **表示データをダウンロード**：グラフに表示しているデータをそのままCSVで保存します。\n",
"\n**Source:** Japan Institute for Health Security (JIHS, formerly NIID), Infectious Disease Weekly Report (IDWR),\nweekly reports of sentinel-surveillance diseases by prefecture ([link](": "\n**出典：** 国立健康危機管理研究機構（JIHS、旧国立感染症研究所）、感染症発生動向調査週報（IDWR）、\n都道府県別の定点把握対象疾患の週次報告（[リンク](",
")). The unit is reports per\nsentinel site per week. About 5,000 sentinel clinics and hospitals report influenza nationwide. The number differs\nby prefecture and changes from week to week, so per-sentinel values, not raw counts, are comparable across\nprefectures.\n\n**How the data were prepared**\n- The table is written by the IDWR alert report R script: one row per prefecture, week and disease.\n- Each prefecture is placed on a complete weekly grid, so a missing week shows as a gap and cannot shift the C2\n  baseline.\n- Reports per sentinel are floored at zero.\n- Weeks run Monday to Sunday. ": ")）。単位は定点医療機関1か所あたりの週ごとの報告数です。全国で約5,000か所の定点医療機関が\nインフルエンザを報告しています。定点数は都道府県により異なり、週ごとにも変わるため、都道府県間で比較できるのは\n実数ではなく、定点あたりの値です。\n\n**データの準備方法**\n- 表はIDWRアラートレポート用Rスクリプトが出力します（都道府県・週・疾患ごとに1行）。\n- 各都道府県を欠けのない週次の並びに置くため、欠けた週は空白として表示され、C2の基準期間がずれることはありません。\n- 定点あたり報告数は0を下限としています。\n- 週は月曜日から日曜日までです。",
"\n- Geography: one row per prefecture (codes 1 to 47). A national row is never added to a sum; any row with\n  another code is dropped. ": "\n- 地理：都道府県ごとに1行（コード1〜47）。全国の行は合計に加えず、他のコードの行は除外します。",
"\n  The population table uses the same 47 codes and is shown for reference only; no rate in this app divides\n  by it.\n- This copy uses ": "\n  人口表も同じ47コードで、参考表示のみです。本アプリの率の計算には使いません。\n- C2の出所：",
".\n\n**Diseases and period.** This app covers the 19 sentinel-surveillance diseases in the JIHS provisional yearly\nprefecture file (teiten-tougai), 2026 weeks 1 to 42. Pick the disease in the sidebar. Each disease has a note on\nits sentinel scheme. Influenza and COVID-19 changed in April 2025, when acute respiratory infection (ARI)\nsurveillance began. The other schemes are being checked with JIHS. Public data only.\n\n**Thresholds.** 1.0 report per sentinel site marks the start of the influenza epidemic season. IDWR uses 10 and 30\nper sentinel as the caution and warning levels for public health center areas; this app draws them at prefecture\nlevel for reference. These lines apply to influenza only.\n\n**Limits of the data.** Sentinel reports reflect care-seeking and reporting practice, not incidence. The latest\nweek may be revised. Prefectures with few sentinels show more week-to-week noise. Clinic closures around New Year\nlower reports in weeks 52 and 1.\n\n**New Year weeks.** The clinic closures around New Year lower reports in weeks 52, 53 and 1, and the rebound\nafterward can look like a sudden rise. By default this app leaves weeks 52, 53 and 1 out of every C2 baseline;\nthe remaining baseline weeks are used if at least 5 are left. The Alerts tab shows how many alerts in weeks 2 to 8\nthat removes. The R alert report keeps every week, so its January alerts can differ until it uses the same rule.\n\n**These alerts are retrospective.** C2 here runs on the latest file, in which earlier weeks may have been revised\nafter first publication. A system running in real time would have seen the provisional values each week, and an\nalert could have come later, earlier, or not at all. The alert threshold of 3 and the ": "。\n\n**疾患と期間** 本アプリは、JIHSの年間暫定の都道府県別ファイル（定点当たり）にある定点把握対象の19疾患を、\n2026年1〜42週について扱います。サイドバーで疾患を選びます。各疾患には定点の枠組みに関する注記があります。\nインフルエンザとCOVID-19は、2025年4月に急性呼吸器感染症（ARI）サーベイランスが始まり、枠組みが変わりました。\nその他の疾患の枠組みはJIHSに確認中です。公開データのみを使用しています。\n\n**しきい値** 定点あたり報告数1.0は、インフルエンザの流行シーズンの開始の目安です。IDWRは、保健所管内について\n定点あたり10を注意報、30を警報の水準としています。本アプリではこれらを都道府県単位で参考として描いています。\nこれらの線はインフルエンザにのみ適用されます。\n\n**データの限界** 定点の報告は、発生率ではなく、受診行動と報告の実態を反映します。最新週は修正されることがあります。\n定点の少ない都道府県は、週ごとのばらつきが大きくなります。年末年始の休診により、52週と1週の報告数が減ります。\n\n**年末年始の週** 年末年始の休診により52・53・1週の報告数が減り、その後の戻りが急な上昇に見えることがあります。\n初期設定では、52・53・1週をすべてのC2基準期間から除外します（残りの基準期間が5週以上ある場合）。\nアラートタブで、2〜8週のアラートがこれによりいくつ減るかを確認できます。Rアラートレポートはすべての週を使うため、\n同じルールを採用するまで、1月のアラートが異なることがあります。\n\n**これらのアラートは後ろ向きの分析です** ここでのC2は最新のファイルで計算しており、過去の週は初回の公表後に修正されている\n可能性があります。リアルタイムで運用するシステムは、毎週の暫定値を見ていたはずで、アラートが遅れる、早まる、\nあるいは出ないこともあり得ます。アラートのしきい値3と、誤警報を数える",
"-week window used\nto count false alarms were set while looking at these data. Lead times and false-alarm counts are therefore\nbest-case estimates for how C2 would perform on future seasons, not a measured real-time performance.\n\n**Spatial statistics.** Global Moran's I and local Moran (LISA) from PySAL `esda`, ": "週間の期間は、これらのデータを見ながら決めました。そのため、リードタイムと誤警報数は、今後のシーズンでC2が\nどう働くかについての最良の見積もりであり、リアルタイムでの実測の性能ではありません。\n\n**空間統計** 全体のモランIと局所モラン（LISA）は、PySALの`esda`で、",
" permutations.\nWeights: queen contiguity on the full-resolution prefecture boundaries (dataofjapan/land), with Hokkaido-Aomori,\nOkinawa-Kagoshima and Fukuoka-Yamaguchi added so every prefecture has a neighbor; row-standardized.\n**Alerts.** EARS C2: 7-week baseline (t-9 to t-3), two-week guard, population SD floored at 0.1, at least 5\nbaseline weeks. **Maps.** Prefecture outlines from dataofjapan/land, simplified for display and bundled in\n`static/`, so the maps need no outside download. Population from the 2020 Population Census (e-Stat), shown for\nreference only.\n\n**This copy.** ": "回の順列検定により計算しました。\n重み：高解像度の都道府県境界（dataofjapan/land）に基づくクイーン隣接に、北海道-青森、沖縄-鹿児島、福岡-山口を加え、\nすべての都道府県に隣接が1つ以上あるようにし、行基準化しています。\n**アラート** EARS C2：7週間の基準期間（t-9〜t-3）、2週間のガード、母集団SDの下限0.1、基準期間は5週以上。\n**地図** 都道府県の輪郭はdataofjapan/landのもので、表示用に簡略化して`static/`に同梱しているため、外部からのダウンロードは不要です。\n人口は2020年国勢調査（e-Stat）で、参考表示のみです。\n\n**このコピー** ",
"\n\n**Built with** Python, Streamlit, pandas, Plotly, PySAL (esda, libpysal). Code: `app.py` ": "\n\n**使用技術** Python、Streamlit、pandas、Plotly、PySAL（esda、libpysal）。コード：`app.py` ",
"High-High": "高-高",
"Low-Low": "低-低",
"High-Low": "高-低",
"Low-High": "低-高",
"Not significant": "有意でない",
"Kinki (Kansai)": "近畿（関西）",
"RSV infection": "RSウイルス感染症",
"Group A streptococcal pharyngitis": "A群溶血性レンサ球菌咽頭炎",
"Herpangina": "ヘルパンギーナ",
"Mycoplasma pneumonia": "マイコプラズマ肺炎",
"30.0 and over": "30.0以上",
"Kanto (Tokyo area)": "関東（東京周辺）",
"Kansai (Osaka area)": "関西（大阪周辺）",
"Okinawa (inset)": "沖縄（挿入図）",
"IDWR levels": "IDWR区分",
"per sentinel": "定点あたり",
"Prefecture": "都道府県",
"Reports per sentinel": "定点あたり報告数",
"Sentinel sites": "定点数",
"Population (2020)": "人口（2020年）",
"Japan IDWR Surveillance Explorer": "日本 IDWRサーベイランス・エクスプローラー",
"Prefectures": "都道府県",
"Add a prefecture": "都道府県を追加",
"Type or pick a prefecture": "都道府県を入力または選択",
"Selected prefectures (click x to remove)": "選択中の都道府県（×で削除）",
"Display options": "表示オプション",
"IDWR week (maps and cards)": "IDWR週（地図とカード）",
"Weeks shown (charts)": "表示する週（グラフ）",
"Chart layout": "グラフの配置",
"One panel per prefecture": "都道府県ごとにパネル",
"Mark C2 alerts on the chart": "グラフにC2アラートを表示",
"Log scale (y-axis)": "対数目盛（縦軸）",
"Leave New Year weeks out of C2 baselines": "年末年始の週をC2基準期間から除外",
"Weekly IDWR Reports by Prefecture in Japan": "日本の都道府県別週次IDWR報告",
"Spatial Statistics": "空間統計",
"Prefecture Map": "都道府県マップ",
"Summary Table": "集計表",
"User Guide": "使い方",
"About the Data": "データについて",
"Global Moran's I": "全体のモランI",
"Permutation p-value": "順列検定のp値",
"High-High prefectures": "高-高の都道府県",
"Prefectures in analysis": "解析対象の都道府県",
"Similar levels sit together": "似た水準が隣り合っている",
"No clear spatial pattern": "明確な空間パターンなし",
"Standardized reports per sentinel (z)": "標準化した定点あたり報告数（z）",
"Spatial lag of z (neighbors' mean)": "空間ラグ（隣接都道府県の平均のz）",
"**Moran scatterplot**": "**モラン散布図**",
"Download the plotted data (CSV)": "表示データをダウンロード（CSV）",
"Kanto and Kansai": "関東と関西",
"Shade prefectures by": "都道府県の色分け",
"Continuous": "連続",
"Outline prefectures with a C2 alert this week (black)": "今週C2アラートが出た都道府県を枠線で表示（黒）",
"Region of each selected prefecture": "選択した都道府県の地域",
"Alert threshold (standard deviations above baseline)": "アラートのしきい値（基準より何標準偏差上か）",
"Alert weeks in window": "期間内のアラート週数",
"Weeks in window": "期間内の週数",
"First alert": "最初のアラート",
"Largest C2": "C2の最大値",
"Week of largest C2": "C2が最大の週",
"Below 1.0, then crossed": "1.0未満から上昇",
"Reports per sentinel, ": "定点あたり報告数、",
"Alert weeks": "アラート週数",
"Table shows": "表示対象",
"All 47 prefectures": "全47都道府県",
"Selected prefectures": "選択した都道府県",
"Lead (weeks)": "リード（週）",
"Onset (sustained 1.0)": "流行開始（1.0を継続して上回る）",
"First C2 alert": "最初のC2アラート",
"Reached 1.0": "1.0に到達",
"Alert came first": "アラートが先行",
"Median lead": "リードの中央値",
"No prefecture with a lead": "リードのある都道府県なし",
"False alarms": "誤警報",
"This app uses public IDWR data only. The TriNetX pediatric influenza data used in the JSPID comparison is not included, because it is not public data. If it becomes available for sharing, it will be added here.": "本アプリは公開されているIDWRデータのみを使用しています。JSPIDでの比較に用いたTriNetXの小児インフルエンザデータは、公開データではないため含まれていません。共有が可能になった場合は、ここに追加します。",
"**Sample data, not real.** Every number, chart and map on this page comes from a synthetic file made for layout. Nothing here describes influenza in Japan. Load data/idwr_weekly.csv from the R script before sharing or deploying.": "**サンプルデータであり、実データではありません。** このページのすべての数値、グラフ、地図は、レイアウト確認用の合成ファイルによるものです。日本のインフルエンザの状況を表すものではありません。共有または公開の前に、Rスクリプトが出力する data/idwr_weekly.csv を読み込んでください。",
".\n\n**Thresholds.** 1.0 report per sentinel site marks the start of the influenza epidemic season. IDWR uses 10 and 30\nper sentinel as the caution and warning levels for public health center areas; this app draws them at prefecture\nlevel for reference. These lines apply to influenza only.\n\n**Limits of the data.** Sentinel reports reflect care-seeking and reporting practice, not incidence. The latest\nweek may be revised. Prefectures with few sentinels show more week-to-week noise. Clinic closures around New Year\nlower reports in weeks 52 and 1.\n\n**New Year weeks.** The clinic closures around New Year lower reports in weeks 52, 53 and 1, and the rebound\nafterward can look like a sudden rise. By default this app leaves weeks 52, 53 and 1 out of every C2 baseline;\nthe remaining baseline weeks are used if at least 5 are left. The Alerts tab shows how many alerts in weeks 2 to 8\nthat removes. The R alert report keeps every week, so its January alerts can differ until it uses the same rule.\n\n**These alerts are retrospective.** C2 here runs on the latest file, in which earlier weeks may have been revised\nafter first publication. A system running in real time would have seen the provisional values each week, and an\nalert could have come later, earlier, or not at all. The alert threshold of 3 and the ": "。\n\n**しきい値** 定点あたり報告数1.0は、インフルエンザの流行シーズンの開始の目安です。IDWRは、保健所管内について\n定点あたり10を注意報、30を警報の水準としています。本アプリではこれらを都道府県単位で参考として描いています。\nこれらの線はインフルエンザにのみ適用されます。\n\n**データの限界** 定点の報告は、発生率ではなく、受診行動と報告の実態を反映します。最新週は修正されることがあります。\n定点の少ない都道府県は、週ごとのばらつきが大きくなります。年末年始の休診により、52週と1週の報告数が減ります。\n\n**年末年始の週** 年末年始の休診により52・53・1週の報告数が減り、その後の戻りが急な上昇に見えることがあります。\n初期設定では、52・53・1週をすべてのC2基準期間から除外します（残りの基準期間が5週以上ある場合）。\nアラートタブで、2〜8週のアラートがこれによりいくつ減るかを確認できます。Rアラートレポートはすべての週を使うため、\n同じルールを採用するまで、1月のアラートが異なることがあります。\n\n**これらのアラートは後ろ向きの分析です** ここでのC2は最新のファイルで計算しており、過去の週は初回の公表後に修正されている\n可能性があります。リアルタイムで運用するシステムは、毎週の暫定値を見ていたはずで、アラートが遅れる、早まる、\nあるいは出ないこともあり得ます。アラートのしきい値3と、誤警報を数える",
"Method: EARS C2 (CDC Early Aberration Reporting System). Baseline = the 7 weeks ending three weeks before the week being tested (t-9 to t-3), leaving a two-week guard (t-2 and t-1). C2 = (reports per sentinel - baseline mean) / baseline SD, using the population SD with a floor of 0.1 and at least 5 baseline weeks. These are the same rules as the IDWR alert report R script. Dashed line: epidemic threshold, 1.0. A false alarm is an alert below 1.0 with no week at 1.0 or above in that week or the next ": "方法：EARS C2（CDCの早期異常検知システム）。基準期間は、検査する週の3週前までの7週間（t-9〜t-3）で、t-2とt-1は2週間のガードです。C2 =（定点あたり報告数 −基準期間の平均）／基準期間のSD。SDは母集団SDで、下限を0.1とし、基準期間は5週以上が必要です。IDWRアラートレポートのRスクリプトと同じルールです。破線：",
"epidemic threshold, 1.0. A false alarm is an alert below 1.0 with no week at 1.0 or above in that week or the next ": "流行の基準、1.0。誤警報とは、1.0未満のアラートのうち、その週と以降"
},
"pref": {
"Hokkaido": "北海道",
"Aomori": "青森",
"Iwate": "岩手",
"Miyagi": "宮城",
"Akita": "秋田",
"Yamagata": "山形",
"Fukushima": "福島",
"Ibaraki": "茨城",
"Tochigi": "栃木",
"Gunma": "群馬",
"Saitama": "埼玉",
"Chiba": "千葉",
"Tokyo": "東京",
"Kanagawa": "神奈川",
"Niigata": "新潟",
"Toyama": "富山",
"Ishikawa": "石川",
"Fukui": "福井",
"Yamanashi": "山梨",
"Nagano": "長野",
"Gifu": "岐阜",
"Shizuoka": "静岡",
"Aichi": "愛知",
"Mie": "三重",
"Shiga": "滋賀",
"Kyoto": "京都",
"Osaka": "大阪",
"Hyogo": "兵庫",
"Nara": "奈良",
"Wakayama": "和歌山",
"Tottori": "鳥取",
"Shimane": "島根",
"Okayama": "岡山",
"Hiroshima": "広島",
"Yamaguchi": "山口",
"Tokushima": "徳島",
"Kagawa": "香川",
"Ehime": "愛媛",
"Kochi": "高知",
"Fukuoka": "福岡",
"Saga": "佐賀",
"Nagasaki": "長崎",
"Kumamoto": "熊本",
"Oita": "大分",
"Miyazaki": "宮崎",
"Kagoshima": "鹿児島",
"Okinawa": "沖縄"
},
"dis": {
"Influenza": "インフルエンザ",
"RSV infection": "RSウイルス感染症",
"Pharyngoconjunctival fever": "咽頭結膜熱",
"Group A streptococcal pharyngitis": "A群溶血性レンサ球菌咽頭炎",
"Infectious gastroenteritis": "感染性胃腸炎",
"Chickenpox": "水痘",
"Hand, foot and mouth disease": "手足口病",
"Erythema infectiosum": "伝染性紅斑",
"Exanthem subitum": "突発性発しん",
"Herpangina": "ヘルパンギーナ",
"Mumps": "流行性耳下腺炎",
"Acute hemorrhagic conjunctivitis": "急性出血性結膜炎",
"Epidemic keratoconjunctivitis": "流行性角結膜炎",
"Bacterial meningitis": "細菌性髄膜炎",
"Aseptic meningitis": "無菌性髄膜炎",
"Mycoplasma pneumonia": "マイコプラズマ肺炎",
"Chlamydial pneumonia": "クラミジア肺炎",
"Rotavirus gastroenteritis": "ロタウイルス胃腸炎",
"COVID-19": "新型コロナウイルス感染症（COVID-19）"
},
"regions": {
"Hokkaido": "北海道",
"Tohoku": "東北",
"Kanto": "関東",
"Chubu": "中部",
"Kansai": "関西",
"Kinki": "近畿",
"Chugoku": "中国",
"Shikoku": "四国",
"Kyushu": "九州"
}
}

EXACT = dict(DATA["exact"])
FRAG = dict(DATA["frag"])
PREF = DATA["pref"]
DIS = DATA["dis"]
REGIONS = DATA["regions"]
EXACT.update(PREF)
EXACT.update(DIS)
EXACT.update({"English": "English", "Alert": "アラート", "Yes": "はい", "No": "いいえ"})

# Phrases whose word order changes in Japanese (numbers are kept).
REGEX = [
    (r"Weeks (\S+) to (\S+) \(set with Weeks shown in the sidebar\)\.", r"\1〜\2の週（サイドバーの「表示する週」で設定）。"),
    (r"second rule\.", "2つ目（除外した場合）のルールを使っています。"),
    (r"first rule\.", "1つ目（含めた場合）のルールを使っています。"),
    (r"(\d+) of (\d+)", r"\1 / \2"),
    (r"Range (-?\d+) to (-?\d+) weeks before onset", r"流行開始の\1〜\2週前"),
    (r"(\d+) weeks? before", r"\1週前"),
    (r"(\d+) weeks? after", r"\1週後"),
    (r"the same week", "同じ週"),
    (r"From (.+?) onset<br>to (.+)", r"流行開始の\1<br>から\2"),
    (r"(\d{4}-W\d+) to (\d{4}-W\d+)", r"\1〜\2"),
    (r"The four cards summarize all 47 prefectures\.", "4つのカードは全47都道府県を集計しています。"),
    (r"Up to (\d+) prefectures can be compared at once\. Remove one first\.", r"同時に比較できるのは最大\1都道府県です。先にどれかを削除してください。"),
    (r"(\d+) rows with codes outside 1 to 47 were dropped", r"\1件の行は、都道府県コードが1〜47の範囲外のため除外しました"),
    (r"(ピーク [\d.]+) in (\d{4}-W\d+)", r"\1（\2）"),
    (r"\bEpidemic\b", "流行"),
    (r"\bCaution\b", "注意報"),
    (r"\bWarning\b", "警報"),
    (r"(-?\d+) weeks\b", r"\1週"),
    (r"(-?\d+) week\b", r"\1週"),
]
_REGEX = [(re.compile(p), r) for p, r in REGEX]
_FRAG_KEYS = sorted(FRAG, key=len, reverse=True)
_NAMES = {**REGIONS, **PREF, **DIS, "influenza": "インフルエンザ", **{k.lower(): v for k, v in DIS.items() if k.lower() != k}}
_NAME_RE = re.compile(r"(?<![A-Za-z0-9])(" + "|".join(sorted(map(re.escape, _NAMES), key=len, reverse=True)) + r")(?![A-Za-z0-9])")


def is_ja():
    try:
        return st.session_state.get("lang") == "日本語"
    except Exception:
        return False


@functools.lru_cache(maxsize=8192)
def _tr(s):
    if s in EXACT:
        return EXACT[s]
    core = s.strip()
    if core and core in EXACT:
        return s.replace(core, EXACT[core])
    if s in FRAG:
        return FRAG[s]
    out = s
    for k in _FRAG_KEYS:
        if k in out:
            out = out.replace(k, FRAG[k])
    if "<" in out:
        out = re.sub(r">([^<>]+)<", lambda m: ">" + EXACT.get(m.group(1), m.group(1)) + "<", out)
    for pat, rep in _REGEX:
        out = pat.sub(rep, out)
    if re.search(r"[A-Za-z]", out):
        out = _NAME_RE.sub(lambda m: _NAMES[m.group(1)], out)
    return out


def T(s):
    """Translate one string when the page is in Japanese; anything else passes through."""
    if not isinstance(s, str) or not s.strip() or not is_ja():
        return s
    return _tr(s)


def _cell(v):
    return EXACT.get(v, v) if isinstance(v, str) else v


_PLOT_KEYS = {"text", "hovertext", "hovertemplate", "name", "ticktext", "title", "customdata",
              "label", "labels", "legendgrouptitle", "annotations"}


def _walk(o, on=False):
    if isinstance(o, str):
        return _tr(o) if on else o
    if isinstance(o, dict):
        return {k: _walk(v, on or k in _PLOT_KEYS) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_walk(v, on) for v in o]
    if hasattr(o, "tolist") and getattr(o, "dtype", None) is not None and o.dtype.kind in "OU":
        return [_walk(v, on) for v in o.tolist()]
    return o


def _plotly(fig):
    try:
        import plotly.graph_objects as go
        return go.Figure(_walk(fig.to_plotly_json()))
    except Exception:
        return fig


def _frame(df, config):
    import pandas as pd
    if not isinstance(df, pd.DataFrame):
        return df, config
    out = df.copy()
    for c in out.columns:
        if out[c].dtype == object or pd.api.types.is_string_dtype(out[c]):
            out[c] = out[c].map(_cell)
    out.columns = [T(c) if isinstance(c, str) else c for c in out.columns]
    if isinstance(config, dict):
        new = {}
        for k, v in config.items():
            if isinstance(v, dict):
                v = {kk: (T(vv) if kk in ("label", "help") and isinstance(vv, str) else vv) for kk, vv in v.items()}
            new[T(k) if isinstance(k, str) else k] = v
        config = new
    return out, config


_TEXT = {"markdown", "write", "caption", "info", "warning", "error", "success", "title", "header",
         "subheader", "button", "checkbox", "toggle", "download_button", "slider", "select_slider",
         "radio", "selectbox", "multiselect", "tabs", "dataframe", "plotly_chart"}
_CHOICE = {"radio", "selectbox", "multiselect", "select_slider"}


def _args(name, a, k):
    a, k = list(a), dict(k)
    if name == "tabs":
        if a:
            a[0] = [T(x) for x in a[0]]
        return a, k
    if name == "dataframe":
        if a:
            a[0], cfg = _frame(a[0], k.get("column_config"))
            if cfg is not None:
                k["column_config"] = cfg
        return a, k
    if name == "plotly_chart":
        if a:
            a[0] = _plotly(a[0])
        return a, k
    if a and isinstance(a[0], str):
        a[0] = T(a[0])
    for key in ("help", "placeholder", "label"):
        if isinstance(k.get(key), str):
            k[key] = T(k[key])
    if name in _CHOICE:
        ff = k.get("format_func")

        def show(x, ff=ff):
            v = ff(x) if ff else x
            return T(v) if isinstance(v, str) else v

        k["format_func"] = show
    return a, k


def _wrap(name):
    orig = getattr(_DG, name)
    if getattr(orig, "_i18n", False):
        return

    @functools.wraps(orig)
    def w(self, *a, **k):
        if is_ja():
            a, k = _args(name, a, k)
        return orig(self, *a, **k)

    w._i18n = True
    setattr(_DG, name, w)
    setattr(st, name, getattr(st._main, name))


def install():
    """Patch Streamlit once; every call after that is a no-op."""
    for n in _TEXT:
        _wrap(n)
    if not getattr(st.set_page_config, "_i18n", False):
        orig = st.set_page_config

        @functools.wraps(orig)
        def spc(*a, **k):
            if is_ja() and isinstance(k.get("page_title"), str):
                k["page_title"] = T(k["page_title"])
            return orig(*a, **k)

        spc._i18n = True
        st.set_page_config = spc


def init_language():
    """Set the starting language once per session: English, or Japanese with ?lang=ja."""
    if "lang" not in st.session_state:
        want = str(st.query_params.get("lang", "")).lower()
        st.session_state["lang"] = "日本語" if want in ("ja", "jp", "japanese") else "English"


def language_switch():
    st.radio("Language / 言語", ["English", "日本語"], key="lang", horizontal=True)
