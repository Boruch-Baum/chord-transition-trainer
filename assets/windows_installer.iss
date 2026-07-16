#define MyAppName "Chord Transition Trainer"
#define MyAppVersion "1.0.0"
#define MyAppExeName "chord-transition-trainer.exe"
#define MyAppSetupName "ChordTransitionTrainerSetup"
#define MyOutputDir "dist"

[Setup]
AppId={{abe66733-1c33-4c48-80a1-223fd64e2c49}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir={# MyOutputDir}
OutputBaseFilename={#MyAppSetupName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
