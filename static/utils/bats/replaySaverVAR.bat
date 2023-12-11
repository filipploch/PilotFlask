@echo off

for /f "delims=" %%a in ('wmic OS Get localdatetime ^| find "."') do set DateTime=%%a

set Yr=%DateTime:~0,4%
set Mon=%DateTime:~4,2%
set Day=%DateTime:~6,2%
set Hr=%DateTime:~8,2%
set Min=%DateTime:~10,2%
set Sec=%DateTime:~12,2%

for /f "tokens=1,2" %%a in ('php C:\xampp\htdocs\query.php') do (
    set "ScoreA=%%a"
    set "ScoreB=%%b"
)


set BackupName=R_%Yr%%Mon%%Day%%Hr%%Min%%Sec%___%ScoreA%-%ScoreB%_VAR

copy "C:\Users\Filip\PycharmProjects\PilotFlask\static\video\processed\replay.mp4" "C:\Users\Filip\PycharmProjects\PilotFlask\static\video\replays\%BackupName%.mp4"
copy "C:\Users\Filip\PycharmProjects\PilotFlask\static\video\replays\%BackupName%.mp4" "C:\Users\Filip\PycharmProjects\PilotFlask\static\video\replays\arch\%BackupName%.mp4"