$ErrorActionPreference = "Continue"

Write-Host "Checking command availability..."
Get-Command Rscript, conda, mamba, micromamba, python, pip -ErrorAction SilentlyContinue |
    Select-Object Name, Source, CommandType |
    Format-Table -AutoSize

Write-Host "`nChecking D:\bioinfor Python packages..."
if (Test-Path -LiteralPath "D:\bioinfor\python.exe") {
    @'
import importlib, sys
print(sys.executable)
print(sys.version)
mods = ["scanpy", "anndata", "pandas", "numpy", "matplotlib", "seaborn", "scipy", "sklearn", "statsmodels"]
for m in mods:
    try:
        mod = importlib.import_module(m)
        print(m, getattr(mod, "__version__", "ok"))
    except Exception as e:
        print(m, "MISSING", e)
'@ | & "D:\bioinfor\python.exe" -
} else {
    Write-Host "D:\bioinfor\python.exe not found."
}
