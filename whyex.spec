# Build a standalone one-file executable:
#   pip install pyinstaller && pyinstaller whyex.spec
a = Analysis(
    ["why.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=["rules", "contrib_rules"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="whyex",
    console=True,
    exclude_binaries=False,
    upx=False,
)
