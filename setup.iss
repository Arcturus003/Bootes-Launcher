[Setup]
AppName=Nexus Client
AppVersion=1.0
AppPublisher=Arcturus
DefaultDirName={autopf}\Arcturus\Nexus Client
DefaultGroupName=Nexus Client
UninstallDisplayIcon={app}\main.exe
Compression=lzma2
SolidCompression=yes
OutputDir=build_out
OutputBaseFilename=NexusClient_Setup_v1.0

[Files]
Source: "build_out\main\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\Nexus Client"; Filename: "{app}\main.exe"; Tasks: desktopicon
Name: "{group}\Nexus Client"; Filename: "{app}\main.exe"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
