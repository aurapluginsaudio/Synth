; Instala o plugin VST3 junto com o app e remove na desinstalação.
!macro customInstall
  SetRegView 64
  CreateDirectory "$COMMONFILES64\VST3"
  RMDir /r "$COMMONFILES64\VST3\AURA Synth Bass.vst3"
  CopyFiles /SILENT "$INSTDIR\resources\plugins\AURA Synth Bass.vst3" "$COMMONFILES64\VST3"
!macroend
!macro customUnInstall
  SetRegView 64
  RMDir /r "$COMMONFILES64\VST3\AURA Synth Bass.vst3"
!macroend
