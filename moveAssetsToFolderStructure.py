import os, sys
from glob import glob
from shutil import copy, rmtree
from zipfile import ZipFile
from pathlib import Path
from iisScriptsLib import read_json_file_direct_utf8, write_json_dumps

if __name__ == "__main__":
    if (len(sys.argv)>1):
        arguments = sys.argv
        for arg in arguments[1:]:
            if 'repository' in arg:
                repository = arg.split('=')[1]
            if 'zipFile' in arg:
                zipFile = arg.split('=')[1]
            if 'inputFolder' in arg:
                inputFolder = arg.split('=')[1]
                
    workDir = f'{inputFolder}/{zipFile.replace(".zip","")}'
    # search for the downloaded zip and unpack it
    with ZipFile(f'{inputFolder}\\{zipFile}', 'r') as zipObj:
        zipObj.extractall(f'{inputFolder}')
        zipObj.close()
    os.remove(f'{inputFolder}\\{zipFile}')
    if os.path.exists(f'{inputFolder}\\interactiveSurveysFiles.zip'):
        with ZipFile(f'{inputFolder}\\interactiveSurveysFiles.zip', 'r') as zipObj:
            zipObj.extractall(f'{inputFolder}')
            zipObj.close()
        os.remove(f'{inputFolder}\\interactiveSurveysFiles.zip')

    # open the json that contains info about the various qex files
    configJson = read_json_file_direct_utf8(f'{workDir}/{repository}-config.json')
    if 'Functionalities' in configJson:
        configJson = configJson['Functionalities']
        
    # take every qex and move it to the correct path ./Askia-iis-production-template/{{FunctionalityName}}/{{Version}}/
    for qex in glob(f'./**/{workDir}/*.qex', recursive=True):
        funcName = Path(qex).stem
        if funcName not in configJson:
            continue
        outputPath = f'{repository}/{funcName}/{configJson[funcName]["Version"]}'
        if os.path.exists(f'{outputPath}/{funcName}.qex'):
            # file is already present from a previews release
            continue
        
        outputPaths = [outputPath, f'{repository}/{funcName}/latest']
        for outPath in outputPaths:
            Path(outPath).mkdir(parents=True, exist_ok=True)
            copy(qex, Path(f'{outPath}/{funcName}.qex'))
            write_json_dumps(str(Path(f'{outPath}/{funcName}-config.json')), {funcName:configJson[funcName]})
            if len(glob(f'./**/{inputFolder}/**/{funcName}_InteractiveConfig.json', recursive=True))>0:
                # we have an interactive surveys config, so copy it next to the functionality
                copy(Path(glob(f'./**/{inputFolder}/**/{funcName}_InteractiveConfig.json',recursive=True)[0]), Path(f'{outPath}/{funcName}_InteractiveConfig.json'))