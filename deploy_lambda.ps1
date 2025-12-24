$ErrorActionPreference = "Stop"

# Configuration
$AccountId = "010469908054"
$Region = "us-east-2"
$RepoName = "weight-planner-lambda"
$EcrUrl = "$AccountId.dkr.ecr.$Region.amazonaws.com"
$ImageUri = "$EcrUrl/$RepoName`:latest"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "AWS Lambda Deployment Script" -ForegroundColor Cyan
Write-Host "Region: $Region"
Write-Host "Repo:   $RepoName"
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Login to ECR
Write-Host "[1/5] Logging in to ECR..." -ForegroundColor Yellow
$LoginCmd = aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $EcrUrl
if ($LASTEXITCODE -ne 0) { Write-Error "Login failed"; exit }
Write-Host "Login successful." -ForegroundColor Green

# 2. Create Repository (if not exists)
Write-Host "`n[2/5] Checking ECR Repository..." -ForegroundColor Yellow
try {
    aws ecr describe-repositories --repository-names $RepoName --region $Region > $null 2>&1
    Write-Host "Repository '$RepoName' already exists." -ForegroundColor Gray
} catch {
    Write-Host "Creating repository '$RepoName'..."
    aws ecr create-repository --repository-name $RepoName --region $Region
    Write-Host "Repository created." -ForegroundColor Green
}

# 3. Build Docker Image
Write-Host "`n[3/5] Building Docker Image (Dockerfile.lambda)..." -ForegroundColor Yellow
docker build -f Dockerfile.lambda -t $RepoName .
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed"; exit }
Write-Host "Build successful." -ForegroundColor Green

# 4. Tag Image
Write-Host "`n[4/5] Tagging Image..." -ForegroundColor Yellow
docker tag "$RepoName`:latest" $ImageUri
Write-Host "Image tagged: $ImageUri" -ForegroundColor Green

# 5. Push Image
Write-Host "`n[5/5] Pushing to ECR..." -ForegroundColor Yellow
docker push $ImageUri
if ($LASTEXITCODE -ne 0) { Write-Error "Push failed"; exit }

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Deployment Artifact Pushed Successfully!" -ForegroundColor Green
Write-Host "Image URI: $ImageUri" -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "`nnext Steps:"
Write-Host "1. Go to AWS Lambda Console"
Write-Host "2. Create/Update Function -> Container Image"
Write-Host "3. Use Image URI: $ImageUri"
