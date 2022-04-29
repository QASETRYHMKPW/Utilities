param (
    [Parameter(Mandatory=$true)][string]$in
 )


 function getMediaDateTaken($filePath,$propertyIndex){
     
    if(!$propertyIndex){
        $propertyIndex=switch -regex ($filePath){
            '(JPG|PNG|GIF|BMP|TIFF|JPEG|HEIC)+$' {12}
            '(MOV|MP4|AVI|MPG|MPEG|WMV|QT|FLV|SWF)+$' {208} # Assuming Windows 10
        }
    }
    try{        
        $shell = New-Object -COMObject Shell.Application
        $shellFolder = $shell.Namespace($(split-path $filePath))
        $shellFile = $shellFolder.ParseName($(split-path $filePath -leaf))
        # How to view all attributes: 0..287|%{'{0}: {1}' -f $_,$shellFolder.GetDetailsOf($shellFile,$_)}
        $dateTakenUnicode=$shellFolder.GetDetailsOf($shellFile, $propertyIndex)
        [datetime]$dateTaken=$dateTakenUnicode -replace '[^\d^\:^\w^\/^\s]'

        return $dateTaken
    }catch{
        return $null
    }
}

[reflection.assembly]::LoadWithPartialName("System.Drawing") | Out-Null

if (-not( Test-Path $in )) {
    Write-Error 'Input directory doest not exits'
}


Get-ChildItem -Path $in -Recurse -File | ForEach-Object -Process {
    $file = $_

    $filePath=$file.FullName
    $fileName=$file.Name
    $dateTaken = getMediaDateTaken $filePath
    $dateSource = 'EXIF'
    if ($dateTaken -eq $null){
        $dateTaken = $file.LastWriteTime
        $dateSource = 'FILE'
    }

    $yearMonth = $dateTaken.ToString('yyyy-MM')

    $oldPath = Split-Path $filePath  -parent
    $newPath = Join-Path -Path $in -ChildPath $yearMonth

    if ( $newPath -ne $oldPath){
        
        if (-not(Test-Path $newPath)){
            New-Item -ItemType Directory -Path $newPath
        }
        $movedPath = Move-Item-AutoRename -Source $filePath -Destination $newPath -Name $fileName
        Write-Output "${filePath},${movedPath},Moved,${dateSource}"
    }else{
        Write-Output "${filePath},${newPath},NotMoved,${dateSource}"
    }
}


Get-ChildItem $Path -Directory -Recurse |
    Where-Object{(Get-ChildItem $_.FullName -File -Recurse).count -eq 0} |
    Remove-Item