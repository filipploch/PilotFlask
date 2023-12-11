@echo off

for /f "delims=" %%a in ('wmic OS Get localdatetime ^| find "."') do set DateTime=%%a

set Yr=%DateTime:~0,4%
set Mon=%DateTime:~4,2%
set Day=%DateTime:~6,2%
set Hr=%DateTime:~8,2%
set Min=%DateTime:~10,2%
set Sec=%DateTime:~12,2%

set BackupName=PowtorkiArchiwum__%Yr%-%Mon%-%Day%_(%Hr%-%Min%-%Sec%)
set FolderName=BackupName
mkdir "D:\Filmy\OBS\Replays\%BackupName%"

copy "C:\Users\Filip\PycharmProjects\PilotFlask\static\video\replays\arch\*.mp4" "D:\Filmy\OBS\Replays\%BackupName%"
del "C:\Users\Filip\PycharmProjects\PilotFlask\static\video\replays\*.mp4"
del "C:\Users\Filip\PycharmProjects\PilotFlask\static\video\replays\arch\*.mp4"