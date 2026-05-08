# build.spec
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.env',    '.'),           # chave da API (fica ao lado do .exe)
        ('Assets',  'Assets'),      # overlay-bg02x.png e ícones
    ],
    hiddenimports=[
        'pystray',
        'pystray._win32',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageTk',
        'PIL.IcoImagePlugin',
        'groq',
        'sounddevice',
        '_sounddevice_data',
        'soundfile',
        'keyboard',
        'pyperclip',
        'pyautogui',
        'scipy',
        'scipy.io',
        'scipy.io.wavfile',
        'numpy',
        'dotenv',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DictationTool',
    debug=False,
    strip=False,
    upx=True,
    console=False,          # sem janela de terminal
    icon='Assets/ICON.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DictationTool',   # pasta de saída: dist/DictationTool/
)
