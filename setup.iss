; MyAppVersion main.py icindeki __version__ ile AYNI olmalidir (bkz. RELEASING.md)
#define MyAppVersion "1.0.0"

[Setup]
AppName=Nexus Client
AppVersion={#MyAppVersion}
AppPublisher=Arcturus
DefaultDirName={autopf}\Arcturus\Nexus Client
DefaultGroupName=Nexus Client
UninstallDisplayIcon={app}\main.exe
Compression=lzma2
SolidCompression=yes
OutputDir=build_out
OutputBaseFilename=NexusClient_Setup_v{#MyAppVersion}
CloseApplications=yes
RestartApplications=no

[Files]
Source: "build_out\main\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\Nexus Client"; Filename: "{app}\main.exe"; Tasks: desktopicon
Name: "{group}\Nexus Client"; Filename: "{app}\main.exe"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
; Normal kurulumda: son ekranda "Nexus Client'i baslat" secenegi
Filename: "{app}\main.exe"; WorkingDir: "{app}"; Description: "Nexus Client'ı başlat"; Flags: nowait postinstall skipifsilent
; Otomatik (sessiz) guncellemeden sonra uygulamayi yeniden ac
Filename: "{app}\main.exe"; WorkingDir: "{app}"; Flags: nowait postinstall skipifnotsilent runasoriginaluser
