rm -r "dist/"
python -m PyInstaller --name tsukushi -F src/main.py
cp -v "src/tsukushi.kv" "dist/"
cp -v -r "src/resources/" "dist/resources/"
