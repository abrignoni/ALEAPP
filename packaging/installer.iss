; Inno Setup script for ALEAPP  (https://jrsoftware.org/isdl.php)
;   python packaging\build.py installer      (passes /DAppVer and /DAppVerNumeric from scripts\version_info.py)
; Expects a one-folder PyInstaller build at dist\ALEAPP\, holding aleapp.exe

#define AppName "ALEAPP"
#ifndef AppVer
  #error Pass the version in with /DAppVer=<version>. packaging\build.py reads it from scripts\version_info.py and does this for you.
#endif
#ifndef AppVerNumeric
  #error Pass the numeric part of the version in with /DAppVerNumeric=<n.n.n>. packaging\build.py does this for you.
#endif
#define AppPublisher "Alexis Brignoni"
; One executable: started without arguments, as the shortcuts start it, it opens the
; window; given arguments it is the command line.
#define AppExe "aleapp.exe"

[Setup]
AppId={{38313423-E48E-4EC1-940F-B8A59F6552B7}
AppName={#AppName}
AppVersion={#AppVer}
; Windows keeps only numbers in a file's version resource, so -dev and the like stay out of it.
VersionInfoVersion={#AppVerNumeric}
AppPublisher={#AppPublisher}
AppPublisherURL=https://github.com/abrignoni/ALEAPP
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=ALEAPP-Setup-{#AppVer}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=aleapp.ico
UninstallDisplayIcon={app}\{#AppExe}
#ifdef AppArm64
; packaging\build.py passes AppArm64 when it runs on ARM64 Windows. That build runs only
; there, and x64compatible would let an x64 machine install it too.
ArchitecturesAllowed=arm64
ArchitecturesInstallIn64BitMode=arm64
#else
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
#endif
PrivilegesRequiredOverridesAllowed=dialog
#ifdef SignToolName
; Signs the installer and its uninstaller at compile time with the Sign Tool configured
; under this name in Inno Setup (Tools > Configure Sign Tools). build.py installer
; --sign-tool <name> passes it in. aleapp.exe inside must already be signed.
SignTool={#SignToolName}
SignedUninstaller=yes
#endif

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "..\dist\ALEAPP\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
