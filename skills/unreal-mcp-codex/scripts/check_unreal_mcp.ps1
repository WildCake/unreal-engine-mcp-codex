param(
    [string]$Path = ".",
    [int]$Port = 8000,
    [string]$UrlPath = "/mcp",
    [switch]$SkipHttp
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-Directory {
    param([string]$InputPath)

    $resolved = Resolve-Path -LiteralPath $InputPath -ErrorAction Stop
    $item = Get-Item -LiteralPath $resolved.Path
    if ($item.PSIsContainer) {
        return $item.FullName
    }

    return $item.Directory.FullName
}

function Test-UnrealRoot {
    param([string]$Directory)

    $projectFiles = @(Get-ChildItem -LiteralPath $Directory -Filter "*.uproject" -File -ErrorAction SilentlyContinue)
    if ($projectFiles.Count -gt 0) {
        return $true
    }

    foreach ($marker in @("GenerateProjectFiles.bat", "GenerateProjectFiles.sh", "GenerateProjectFiles.command")) {
        if (Test-Path -LiteralPath (Join-Path $Directory $marker) -PathType Leaf) {
            return $true
        }
    }

    return $false
}

function Find-UnrealRoot {
    param([string]$StartDirectory)

    $directory = Get-Item -LiteralPath $StartDirectory
    while ($null -ne $directory) {
        if (Test-UnrealRoot -Directory $directory.FullName) {
            return $directory.FullName
        }

        $parent = $directory.Parent
        if ($null -eq $parent -or $parent.FullName -eq $directory.FullName) {
            break
        }

        $directory = $parent
    }

    return $null
}

function Get-ModelContextProtocolState {
    param([string[]]$ProjectFiles)

    $states = @()
    foreach ($projectFile in $ProjectFiles) {
        try {
            $json = Get-Content -LiteralPath $projectFile -Raw | ConvertFrom-Json
            $plugin = $null
            if ($null -ne $json.Plugins) {
                $plugin = @($json.Plugins) | Where-Object { $_.Name -eq "ModelContextProtocol" } | Select-Object -First 1
            }

            $states += [pscustomobject]@{
                path = $projectFile
                present = $null -ne $plugin
                enabled = if ($null -ne $plugin -and $plugin.PSObject.Properties.Name -contains "Enabled") { [bool]$plugin.Enabled } else { $false }
            }
        }
        catch {
            $states += [pscustomobject]@{
                path = $projectFile
                present = $false
                enabled = $false
                error = $_.Exception.Message
            }
        }
    }

    return $states
}

function Get-EditorSettingsState {
    param([string]$ProjectRoot)

    $settingsFiles = @(Get-ChildItem -LiteralPath (Join-Path $ProjectRoot "Saved\Config") -Filter "EditorPerProjectUserSettings.ini" -Recurse -File -ErrorAction SilentlyContinue)
    $states = @()
    foreach ($file in $settingsFiles) {
        $text = Get-Content -LiteralPath $file.FullName -Raw
        $states += [pscustomobject]@{
            path = $file.FullName
            hasModelContextProtocolSection = $text -match "\[/Script/ModelContextProtocolEngine\.ModelContextProtocolSettings\]"
            autoStart = $text -match "(?m)^\s*bAutoStartServer\s*=\s*True\s*$"
            port = if ($text -match "(?m)^\s*ServerPortNumber\s*=\s*(\d+)\s*$") { [int]$Matches[1] } else { $null }
            urlPath = if ($text -match "(?m)^\s*ServerUrlPath\s*=\s*(\S+)\s*$") { $Matches[1] } else { $null }
            toolSearch = if ($text -match "(?m)^\s*bEnableToolSearch\s*=\s*(True|False)\s*$") { $Matches[1] } else { $null }
        }
    }

    return $states
}

function Test-McpEndpoint {
    param([string]$Url)

    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 3 -UseBasicParsing
        return [pscustomobject]@{
            reachable = $true
            statusCode = [int]$response.StatusCode
            statusDescription = $response.StatusDescription
        }
    }
    catch {
        $statusCode = $null
        if ($null -ne $_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }

        return [pscustomobject]@{
            reachable = $null -ne $statusCode
            statusCode = $statusCode
            error = $_.Exception.Message
        }
    }
}

$startDirectory = Resolve-Directory -InputPath $Path
$projectRoot = Find-UnrealRoot -StartDirectory $startDirectory
$endpointPath = if ($UrlPath.StartsWith("/")) { $UrlPath } else { "/$UrlPath" }
$endpoint = "http://127.0.0.1:$Port$endpointPath"

if ($null -eq $projectRoot) {
    [pscustomobject]@{
        startDirectory = $startDirectory
        projectRoot = $null
        endpoint = $endpoint
        advice = @("No Unreal project root found walking upward from the supplied path.")
    } | ConvertTo-Json -Depth 6
    exit 2
}

$projectFiles = @(Get-ChildItem -LiteralPath $projectRoot -Filter "*.uproject" -File -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
$projectType = if (Test-Path -LiteralPath (Join-Path $projectRoot "Engine") -PathType Container) { "engine-source-or-monorepo" } else { "game-or-installed-engine-project" }
$codexConfig = Join-Path $projectRoot ".codex\config.toml"
$mcpJson = Join-Path $projectRoot ".mcp.json"
$editorSettings = @(Get-EditorSettingsState -ProjectRoot $projectRoot)
$pluginState = @(Get-ModelContextProtocolState -ProjectFiles $projectFiles)
$httpState = if ($SkipHttp) { $null } else { Test-McpEndpoint -Url $endpoint }

$advice = New-Object System.Collections.Generic.List[string]
if ($projectFiles.Count -eq 0) {
    $advice.Add("No .uproject file found at the detected root; this may be an Unreal source tree.")
}
if (($pluginState | Where-Object { $_.present -and $_.enabled }).Count -eq 0 -and $projectFiles.Count -gt 0) {
    $advice.Add("Enable ModelContextProtocol in the .uproject or through Edit > Plugins.")
}
if (-not (Test-Path -LiteralPath $codexConfig -PathType Leaf)) {
    $advice.Add("No project .codex/config.toml found at the detected root.")
}
if ($editorSettings.Count -eq 0 -or ($editorSettings | Where-Object { $_.autoStart }).Count -eq 0) {
    $advice.Add("Auto-start was not detected in EditorPerProjectUserSettings.ini.")
}
if (-not $SkipHttp -and $null -ne $httpState -and -not $httpState.reachable) {
    $advice.Add("MCP endpoint was not reachable. Launch Unreal Editor and run ModelContextProtocol.StartServer.")
}

[pscustomobject]@{
    startDirectory = $startDirectory
    projectRoot = $projectRoot
    projectType = $projectType
    uprojectFiles = $projectFiles
    modelContextProtocol = $pluginState
    codexConfig = [pscustomobject]@{
        path = $codexConfig
        exists = Test-Path -LiteralPath $codexConfig -PathType Leaf
    }
    mcpJson = [pscustomobject]@{
        path = $mcpJson
        exists = Test-Path -LiteralPath $mcpJson -PathType Leaf
    }
    editorSettings = $editorSettings
    endpoint = $endpoint
    http = $httpState
    advice = @($advice)
} | ConvertTo-Json -Depth 8
