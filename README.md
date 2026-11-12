# taiwan-news-daily

每日台灣國際新聞摘要：整理世界各國媒體對台灣的報導，每天台北時間 06:00 前更新。

網站：https://kevinlodesign.github.io/taiwan-news-daily/

## 結構

```
data/YYYY-MM-DD.json   每日資料（唯一需要手動或自動新增的檔案）
scripts/build.py       由 data/ 產生 days/*.html 與 index.html
assets/style.css       樣式（含列印／PDF 版面）
days/                  產生的每日頁面
index.html             產生的首頁
```

## 每日更新

```bash
# 新增 data/2026-11-13.json 後
python3 scripts/build.py
git add -A && git commit -m "news: 2026-11-13" && git push
```

## JSON 格式

```json
{
  "date": "2026-11-13",
  "window": "2026-11-12 06:00 – 2026-11-13 05:00（台北時間）",
  "highlights": ["重點一", "重點二", "重點三"],
  "categories": [
    {
      "id": "security", "name": "兩岸與軍事安全",
      "items": [{
        "title": "繁中標題",
        "summary": "2～3 句改寫摘要",
        "prc": false,
        "tag": "選填，例如：持續追蹤",
        "sources": [{"outlet": "Reuters", "time": "11/13 03:10", "url": "https://..."}],
        "local": [{"outlet": "中央社", "note": "報導重點差異", "url": "https://..."}],
        "note": "選填，例如：只找到台灣媒體報導",
        "image": {
          "url": "https://commons.wikimedia.org/wiki/Special:FilePath/檔名.jpg?width=960",
          "credit": "圖說｜攝影：作者｜授權",
          "source": "https://commons.wikimedia.org/wiki/File:檔名.jpg"
        }
      }]
    }
  ],
  "search_notes": {"not_found": ["..."], "paywalled": ["..."]}
}
```

分類 id 固定為 6 類：

| id | 名稱 |
|---|---|
| `security` | 兩岸與軍事安全 |
| `diplomacy` | 國際外交 |
| `finance` | 經濟財經 |
| `semiconductor` | 半導體與供應鏈 |
| `tech` | 科技與產業 |
| `society` | 社會、文化、觀光、運動 |

## 配圖

- `image` 選填。只用 Wikimedia Commons 上的自由授權圖（CC BY、CC BY-SA、CC0、公有領域），credit 必須寫作者與授權。
- 不使用新聞媒體或通訊社的照片，也不使用以可辨識人物為主體的照片。
- 沒有 `image`，或圖片載入失敗時，自動顯示 `assets/cat/<分類 id>.svg` 分類主視覺。
