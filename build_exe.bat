@echo off
echo ========================================
echo AARO ERP - PDKS EXE Olusturucu
echo ========================================
echo.

echo 1. PyInstaller yukleniyor...
pip install pyinstaller

echo.
echo 2. Gerekli kutuphaneler kontrol ediliyor...
pip install -r requirements.txt

echo.
echo 3. Onceki build dosyalari temizleniyor...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo.
echo 4. EXE dosyasi olusturuluyor...
pyinstaller build_exe.spec

echo.
echo 5. Sonuc kontrol ediliyor...
if exist "dist\AARO_ERP_PDKS.exe" (
    echo ========================================
    echo ✅ BASARILI! EXE dosyasi olusturuldu!
    echo ========================================
    echo.
    echo Dosya konumu: dist\AARO_ERP_PDKS.exe
    echo Dosya boyutu:
    dir "dist\AARO_ERP_PDKS.exe" | find "AARO_ERP_PDKS.exe"
    echo.
    echo EXE dosyasini test etmek icin:
    echo cd dist
    echo AARO_ERP_PDKS.exe
    echo.
    echo Dagitim icin 'dist' klasorundeki tum dosyalari kopyalayin.
) else (
    echo ========================================
    echo ❌ HATA! EXE dosyasi olusturulamadi!
    echo ========================================
    echo.
    echo Hata loglarini kontrol edin:
    echo - build.log dosyasini inceleyin
    echo - Python ve kutuphanelerin yuklu oldugunu kontrol edin
    echo - Antivirus yaziliminin engelleme yapmadigi kontrol edin
)

echo.
echo 6. Temizlik yapiliyor...
if exist "__pycache__" rmdir /s /q "__pycache__"
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

echo.
echo ========================================
echo Islem tamamlandi!
echo ========================================
pause
