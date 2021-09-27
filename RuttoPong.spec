# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew, gstreamer

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\emaca\\Desktop\\NIMEI(TBS)\\RuttoPong'],
             binaries=[],
             datas=[],
             hiddenimports=['kivy'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
#splash = Splash('data/pre.png',
                #binaries=a.binaries,
                #datas=a.datas,
                #text_pos=None,
                #text_size=12,
                #minify_script=True)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
		  Tree('data/'),
		  Tree('./'),
		  *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins +  gstreamer.dep_bins)],
          a.zipfiles,
          a.datas,
          #splash, 
          #splash.binaries,
          [],
          name='RuttoPong',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='data\\icon.ico')
