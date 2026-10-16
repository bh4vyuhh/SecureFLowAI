try {
    $word = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Word.Application")
    $found = $false
    for ($i = $word.Documents.Count; $i -ge 1; $i--) {
        $doc = $word.Documents.Item($i)
        Write-Output "Open doc: $($doc.FullName)"
        if ($doc.Name -like "*SecureFlowAI*") {
            Write-Output "Closing: $($doc.FullName)"
            $doc.Close([ref]$false)
            $found = $true
        }
    }
    if (-not $found) {
        Write-Output "No SecureFlowAI doc open in Word."
    }
} catch {
    Write-Output "Error: $_"
}
