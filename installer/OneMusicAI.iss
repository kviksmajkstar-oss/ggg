#define MyAppName "OneMusic AI"
#define MyAppPublisher "OneMusic"
#define MyAppExeName "run_onemusic.bat"
#ifndef AppVersion
  #define AppVersion "1.0.1"
#endif

[Setup]
AppId={{F1F6D95D-1DB8-4E6B-9EA8-08E66E9BE3D7}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\OneMusic AI
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=OneMusicAI-Setup-{#AppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\OneMusicAI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустить OneMusic AI"; Flags: postinstall shellexec skipifsilent
