$Root = pwd
$PythonVersion = "3.9.6"
$PythonPth = "python39._pth"
$PythonExe = "$Root\python\python"

wget https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip -O python-$PythonVersion-embed-amd64.zip
wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py

Expand-Archive -Force python-$PythonVersion-embed-amd64.zip python
rm ".\python\$PythonPth"

.\python\python .\get-pip.py

.\python\Scripts\pip install -r ..\requirements.txt
.\python\Scripts\pip install PySimpleGUIWx

cd ..
Invoke-Expression "$PythonExe makecard.py"
Invoke-Expression "$PythonExe makerarity.py"
