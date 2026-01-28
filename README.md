# TextLayer

TextLayer is a desktop tool for adding an OCR text layer to image-only scanned PDFs. It runs fully offline on your machine and outputs a new PDF without modifying the original file.

## Features
- Drag & drop or browse to select a PDF
- Outputs a new PDF with a text layer (OCR)
- Detects input states and behaves accordingly:
  1) Image-only PDF -> OCR to add text layer
  2) Text-only PDF -> show message, no conversion
  3) Image + text PDF -> ask whether to re-OCR (rebuild text layer)
  4) Encrypted/signed PDF -> reject conversion
  5) Non-PDF file -> reject conversion
- Progress indicator with status messages
- Export OCR text to `.txt`
- Language UI: English / Japanese / Simplified Chinese
- OCR language selector: English / Japanese / Simplified Chinese / Traditional Chinese
- Settings persistence (last output directory, last language)
- Logging to `logs/textlayer.log`

## Tech Stack
- Python
- PySide6 (Qt)
- OCRmyPDF
- Tesseract OCR (via pytesseract)
- pikepdf + PyMuPDF for file inspection

## Install (Windows focus)

### 1) Create and activate a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2) Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3) Install Tesseract OCR
- Download and install from the official Tesseract builds for Windows.
- Make sure `tesseract.exe` is in your PATH or set it via Preferences in the app.
- Language packs needed:
  - English: `eng`
  - Japanese: `jpn`
  - Simplified Chinese: `chi_sim`

### 4) Install OCRmyPDF dependencies
OCRmyPDF requires external tools:
- **Ghostscript** (for PDF rendering)
- **QPDF** (for PDF optimization)

On Windows, install the official binaries and ensure their executables are on PATH.

## Run

Option A (recommended):
```bash
python src/main.py
```

Option B (if you set PYTHONPATH=src):
```bash
python -m textlayer
```

## How OCR Works
- OCRmyPDF is used to add a text layer to scanned PDFs.
- For mixed text/image PDFs, you can choose to re-OCR and rebuild the text layer.
- OCR text export uses OCRmyPDF sidecar output; you can save it via ?Save Text As??.

## Settings Storage (QSettings)
- Windows: stored in registry under `HKEY_CURRENT_USER\Software\TextLayer\TextLayer`
- Keys used:
  - `ui/language`
  - `output/last_dir`
  - `ocr/tesseract_path`
  - `ocr/language`

## FAQ

**Why are encrypted or signed PDFs rejected?**
OCRmyPDF cannot safely modify encrypted or signed PDFs without breaking signatures or failing decryption. The tool refuses to process these files.

**The app says Tesseract is missing. What should I do?**
Install Tesseract and ensure `tesseract.exe` is on PATH. You can also set the full path in Preferences.

**Why does the tool skip text-only PDFs?**
Text-only PDFs already contain selectable text, so OCR is unnecessary and could degrade quality.

**I changed the output directory but the output filename is still old.**
Use ?Save As?? to pick a custom output name, or leave it to auto-generate `<name>_textlayer.pdf` in the selected output directory.

## Packaging (Optional)
You can package the app with PyInstaller:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --add-data "assets;assets" src/main.py
```
You may need to bundle Tesseract and OCRmyPDF separately depending on your distribution plan.

## License
This project uses the MIT License by default. Replace if needed.

---


# TextLayer (日本語版)
TextLayer は、画像のみのスキャン済み PDF に OCR テキスト層を追加するオフラインデスクトップツールです。原ファイルは修正せず、新しい PDF を出力します。

## 主な機能
- PDF をドラッグまたは選択して入力
- OCR でテキスト層付き PDF を出力
- 入力 PDF の状態判定：
  1) 画像のみの PDF → OCR 実行
  2) テキストのみの PDF → 変換しない
  3) 画像 + テキスト PDF → 再 OCR 実行を確認
  4) 暗号化/署名付き PDF → 拒否
  5) PDF 以外 → 拒否
- OCR 言語の選択：英語 / 日本語 / 簡体中文 / 繁体中文
- 出力フォルダーと OCR 言語は永続保存
- ログは `logs/textlayer.log` に出力

## 実行
```bash
python src/main.py
```

## 設定保存 (QSettings)
- Windows レジストリ: `HKEY_CURRENT_USER\\Software\\TextLayer\\TextLayer`
- キー:
  - `ui/language`
  - `output/last_dir`
  - `ocr/tesseract_path`
  - `ocr/language`

## ヒント
- OCR 言語が想定と違うときは、上部の OCR Language ドロップダウンで言語を指定してください。
- Tesseract の対応言語パックが必要です。
